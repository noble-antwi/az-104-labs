# Azure Files share

![One file share, three ways in: who gets through, and with what](diagrams/files-access.svg)

*Figure 6.1: Eight steps, each captioned at the top as it happens: SMB blocked from home, portal upload with the key, a snapshot and restore, Entra denied as Owner, read-only with a data role, a VM mounting over SMB, and the VM cut off when keys are switched off. Built by
[`scripts/diagrams/lab06_files_access.py`](../scripts/diagrams/lab06_files_access.py);
video versions: [landscape](diagrams/files-access.mp4) ·
[vertical](diagrams/files-access-vertical.mp4).*

> **Intent:** Stand up an Azure Files SMB share, mount it, snapshot it, and control access with identity instead of storage keys.

> **Status:** done (19 to 21 Nov 2026). Groundwork deployed from Bicep, file share built and tested in the portal, end state rebuilt in Bicep, everything torn down 21 Nov 2026.

> **Method:** from this lab on, groundwork that an earlier lab already built by hand (resource group, storage account, VM) is deployed from Bicep. Portal time goes to what is new: the share, snapshots and access.

## What this lab is

A storage account can hold **file shares**: folders that Windows, Linux and
macOS can map as a network drive over **SMB**, the same protocol as an office
file server. The portal and APIs reach the same share over **HTTPS**. This lab
puts five Biira Bank branch documents in a share, tries to reach it three
ways (a laptop at home, the portal, a VM inside Azure), takes a snapshot and
restores from it, and then moves from the storage key to Entra roles until the
key is switched off altogether.

## Questions

1. **Will a home network let SMB (port 445) through to Azure?**
2. **After a snapshot, a file is changed. What does the snapshot's copy say?**
3. **As Owner, switching the portal from the key to Entra: will the files show?**
4. **With Storage File Data Privileged Reader, will an upload work?**
5. **Will port 445 work from a VM inside Azure?**
6. **With shared key access turned off, does an SMB mount that is already connected keep working? Does a reconnect?**
7. **Can a storage account born with keys off still be opened in the portal?**

### Predictions (written before testing)

| # | My prediction | What actually happened |
|---|---|---|
| 1 | (not answered) | **Blocked.** `TcpTestSucceeded: False` (Figure 6.4). |
| 2 | Version 1: the snapshot is frozen. | **Right.** Snapshot: Version 1, live file: Version 2 (Figures 6.13, 6.14). |
| 3 | No: Owner is management plane only, no data actions. | **Right.** *You do not have permissions to list the data* (Figure 6.18). |
| 4 | No: Reader has no write. | **Right**, once the portal was really using Entra. The first try "worked" because the portal had quietly gone back to the key (Figures 6.22, 6.24). |
| 5 | Yes: Azure does not block 445. | **Right.** `succeeded`, to the same IP that timed out from home (Figure 6.27). |
| 6 | Neither. | **Right.** The open mount died with *Host is down*; the reconnect got *mount error(13): Permission denied* (Figures 6.32, 6.33). |
| 7 | Yes: access comes from the role, not a key. | **Right.** It opened straight into *Microsoft Entra user account* (Figure 6.37). |

## Key ideas, from zero

| Term | Plain meaning |
|---|---|
| **File share** | A folder in a storage account that clients map as a network drive. |
| **SMB (port 445)** | The network-drive protocol. Needs outbound 445 open on the client's network. |
| **File endpoint** | `<account>.file.core.windows.net`: the address of the account's file service. It exists as soon as the account does. |
| **Storage account key** | One of two account-wide passwords (`key1`, `key2`). Whoever holds one can do anything to every share. |
| **Snapshot** | A read-only copy of the whole share at one moment. Stores only what changes afterwards. |
| **Soft delete** | A deleted share can be recovered for N days (7 by default). Whole shares, not single files. |
| **Storage File Data Privileged Reader / Contributor** | Data roles for the portal, CLI and REST (HTTPS). "Privileged" means they ignore file-level permissions. |
| **Storage File Data SMB Share Reader / Contributor** | Data roles for **SMB mounts with an identity**. Need AD DS, Entra Domain Services or Entra Kerberos. |
| **Shared key access** | Account switch. Off means no keys, no key-signed SAS, no key-based SMB. |

## Architecture

![Lab 06 architecture: laptop blocked on 445, the portal over HTTPS with an Entra role, a VM in Azure mounting over SMB with the key, and the Bicep end state](diagrams/architecture.png)

*Figure 6.2: Lab 06 architecture. Source: [`diagrams/architecture.drawio`](diagrams/architecture.drawio).*

## What gets built

| Item | Setting | Built with |
|---|---|---|
| `rg-lab-files`, `stlabfilesnoble01` | StorageV2, LRS, TLS 1.2, keys on at first | Bicep ([`main.bicep`](bicep/main.bicep), [`storage.bicep`](bicep/storage.bicep)) |
| Share `branch-docs` | Transaction optimized, backup off, soft delete 7 days | portal |
| 5 branch files | hours, cash procedure, rota, complaints, `policy.txt` | [`other_files/upload`](other_files/upload) |
| Snapshot | "before policy v2" | portal |
| Role | Storage File Data Privileged Reader, on the account, to me | portal |
| `vm-files-01` | B2ats_v2, Ubuntu 24.04, cifs-utils, SSH from my IP | Bicep ([`vm.bicep`](bicep/vm.bicep)) |
| End state | keys off, Entra default, share, role | Bicep ([`files-iac.bicep`](bicep/files-iac.bicep)) |

## Build it

### 1. Groundwork from Bicep

```powershell
cd 06-azure-files-share\bicep
az deployment sub create -l eastus -n lab06-base -f main.bicep --query properties.outputs
```

Shared key access stays **on** for now: a PC that is not domain-joined can
only mount SMB with the key (Figure 6.3).

![Base deployment outputs](screenshots/06-01-base-bicep-deploy.png)

*Figure 6.3: Resource group and storage account from Bicep; the output is the file endpoint.*

### 2. Can home reach port 445?

Before building anything, test the road, not the room: the file endpoint
exists as soon as the account does.

```powershell
Test-NetConnection stlabfilesnoble01.file.core.windows.net -Port 445
```

`TcpTestSucceeded: False` (Figure 6.4). The home network blocks outbound 445,
so no share setting could make a mapped drive work from here. The endpoint
address is also under **Storage account → Settings → Endpoints**.

![Port 445 blocked from home](screenshots/06-02-port-445-blocked.png)

*Figure 6.4: From home, port 445 times out. Ping failing is normal; Azure does not answer pings.*

### 3. The share

**Data storage → File shares → + File share**: `branch-docs`, **Transaction
optimized**, and **Enable backup unticked** (backup means a Recovery Services
vault, which is lab 11). The overview shows the share URL, **soft delete 7
days**, **0 snapshots**, and **Identity-based access: Not configured**
(Figures 6.5 to 6.7). "Classic file share" means a share inside a storage
account.

![New share, basics](screenshots/06-03-new-share-basics.png)

*Figure 6.5: Name and access tier. Maximum capacity 100 TiB.*

![Backup unticked](screenshots/06-04-new-share-backup-off.png)

*Figure 6.6: Backup off: snapshots are taken by hand instead.*

![Share overview](screenshots/06-05-share-overview.png)

*Figure 6.7: Share URL, soft delete 7 days, identity-based access not configured (subscription ID redacted).*

### 4. Files over HTTPS

**Upload** uses HTTPS on 443, so the home block does not matter. Five files
went up (Figures 6.8, 6.9). Note the line above the list: **Authentication
method: Access key**. The portal read the account key behind the scenes,
which an Owner is allowed to do.

![Uploading five files](screenshots/06-06-upload-five-files.png)

*Figure 6.8: Five files uploaded from the browser (subscription ID redacted).*

![Five files in Browse](screenshots/06-07-browse-five-files.png)

*Figure 6.9: The share in Browse, authentication method: Access key.*

### 5. Snapshot, change, restore

**Operations → Snapshots → + Add snapshot**, comment *before policy v2*. The
name is the moment it was taken, in UTC (Figure 6.10). Automated snapshots
come from Azure Backup (initiator *AzureBackup*), which is lab 11.

![Snapshot taken](screenshots/06-08-snapshot-taken.png)

*Figure 6.10: One manual snapshot.*

`policy.txt` was then changed to *Version 2*. With **Overwrite if files
already exist** unticked, the portal refused (Figure 6.11); ticked, it
replaced the file (Figures 6.12, 6.13).

![Overwrite off refused](screenshots/06-09-overwrite-off-refused.png)

*Figure 6.11: Overwrite off: "The following files already exist" (subscription ID redacted).*

![Overwrite on](screenshots/06-10-overwrite-on.png)

*Figure 6.12: Overwrite ticked.*

![Live file is Version 2](screenshots/06-11-live-file-version-2.png)

*Figure 6.13: The live file now says Version 2.*

Opening the snapshot shows the share as it was: `policy.txt` still says
**Version 1** (Figure 6.14). **Restore** offers *Restore as a copy and
rename* (safer: nothing is overwritten) or *Overwrite original file*
(Figures 6.15, 6.16). Overwrite put Version 1 back (Figure 6.17).

![Snapshot copy is Version 1](screenshots/06-12-snapshot-copy-version-1.png)

*Figure 6.14: Inside the snapshot, policy.txt is still Version 1.*

![Restore options](screenshots/06-13-restore-options.png)

*Figure 6.15: Restore as a copy and rename (default).*

![Overwrite original](screenshots/06-14-restore-overwrite.png)

*Figure 6.16: Overwrite original file.*

![Restored to Version 1](screenshots/06-15-restored-version-1.png)

*Figure 6.17: After the restore, the live file is Version 1 again.*

### 6. Entra instead of the key

**Switch to Microsoft Entra user account** as Owner: *You do not have
permissions to list the data* (Figure 6.18). Owner holds `actions`, not
`dataActions`: it can create and delete the share but not read inside it.
Same split as lab 04.

![Entra denied as Owner](screenshots/06-16-entra-denied-as-owner.png)

*Figure 6.18: Owner, using Entra, cannot list the files.*

**Access control (IAM)** on the storage account → **Storage File Data
Privileged Reader** → me (Figures 6.19 to 6.21). The portal-and-API family of
file data roles; the SMB Share roles are for identity-based mounts.

![Choosing the member](screenshots/06-17-file-reader-members.png)

*Figure 6.19: The role and the member (object ID redacted).*

![Review](screenshots/06-18-file-reader-review.png)

*Figure 6.20: Scope: the storage account (IDs redacted).*

![Assignment in IAM](screenshots/06-19-iam-file-reader-assigned.png)

*Figure 6.21: The data role next to the two inherited Owner assignments.*

The first upload test **worked**, and the screenshot shows why: the portal had
gone back to **Access key** (Figure 6.22). **Configuration → Default to
Microsoft Entra authorization in the Azure portal: Enabled** made Entra stick
(Figure 6.23). With Entra really in use, listing worked and the upload was
refused (Figure 6.24).

![Upload worked via the key](screenshots/06-20-upload-worked-via-access-key.png)

*Figure 6.22: An upload that "worked": authentication method had reverted to Access key.*

![Default to Entra](screenshots/06-21-default-entra-in-portal.png)

*Figure 6.23: Default to Microsoft Entra authorization in the Azure portal: Enabled.*

![Reader upload denied](screenshots/06-22-entra-reader-upload-denied.png)

*Figure 6.24: As Reader, using Entra: list yes, upload denied.*

### 7. SMB from inside Azure

A small Linux VM from [`bicep/vm.bicep`](bicep/vm.bicep): the lab 03 pattern
made smaller, with **cloud-init** installing `cifs-utils` (the Linux SMB
client) at first boot. B1s is no longer offered in East US, so it is
**Standard_B2ats_v2** (Figures 6.25, 6.26).

```powershell
az deployment group create -g rg-lab-files -n lab06-vm -f vm.bicep -p adminPublicKey="$(Get-Content $HOME\.ssh\vm-lab-01.pub)" sshSourceAddress="$((Invoke-RestMethod https://api.ipify.org))/32"
```

![VM deployment](screenshots/06-23-vm-bicep-deploy.png)

*Figure 6.25: The VM deployment output (public IP redacted).*

![cifs-utils installed](screenshots/06-24-cifs-utils-installed.png)

*Figure 6.26: cloud-init installed the SMB client.*

From the VM, port 445 to the **same address** that timed out from home
succeeds (Figure 6.27). The traffic stays on Microsoft's network; giving the
share a private address in the VNet is lab 15.

```bash
nc -zv stlabfilesnoble01.file.core.windows.net 445
```

![Port 445 open from the VM](screenshots/06-25-port-445-open-from-vm.png)

*Figure 6.27: From inside Azure, 445 succeeds.*

**Connect → Linux → Storage account key** generates a mount script (Figure
6.28). It writes the **key in plain text** into
`/etc/smbcredentials/<account>.cred` (username = the account name, password =
the key), adds an `/etc/fstab` line so the share remounts at boot, and mounts
it now (Figure 6.29).

![Connect, Linux](screenshots/06-26-connect-linux.png)

*Figure 6.28: The Connect panel. Outside the share's region, SMB 3.x with encryption is required (subscription ID redacted).*

![Mount script ran](screenshots/06-27-mount-script-ran.png)

*Figure 6.29: The script ran (storage key redacted).*

The six files appear as a normal folder, a new file written over SMB shows up
in the portal over HTTPS, and `df -h` shows a 100T disk (Figures 6.30, 6.31).
Every file reads as owner `root`: the share was mounted as the storage
account, not as a person.

![ls, write, df](screenshots/06-28-smb-ls-write-df.png)

*Figure 6.30: Listing, writing and the mounted share in df.*

![The Linux file in the portal](screenshots/06-29-linux-file-in-portal.png)

*Figure 6.31: from-linux.txt, written over SMB, read over HTTPS.*

### 8. Keys off

**Configuration → Allow storage account key access: Disabled.** The open mount
failed on its next request (*Host is down*), and a reconnect with the key was
refused (*mount error(13): Permission denied*) (Figures 6.32, 6.33). The
portal, using Entra and the Reader role, kept working.

![Existing mount down](screenshots/06-30-keys-off-existing-mount-down.png)

*Figure 6.32: Keys off: the already-connected mount fails at once.*

![Remount denied](screenshots/06-31-keys-off-remount-denied.png)

*Figure 6.33: The reconnect with the key: permission denied.*

The key had appeared in a screenshot, so **key1 was rotated** (Figure 6.34).
Rotation makes a new key and the old one stops working forever; having two
keys lets apps switch to one while the other is rotated.

![key1 rotated](screenshots/06-32-key1-rotated.png)

*Figure 6.34: key1 rotated. The banner: with Shared Key disabled, SAS is denied too.*

## Break it

- **Port 445 from home: blocked.** The most common reason "map the Azure
  file share" fails. Test with `Test-NetConnection` before blaming the share.
- **Upload with Overwrite unticked: refused.** A safety default, not an error.
- **"Reader can upload":** it could not. The portal had silently gone back to
  the key. Check the **Authentication method** line, or set *Default to
  Microsoft Entra authorization*.
- **Keys off with a live mount:** cut off on the next request, not at the next
  reboot.

## Rebuild it as code

The groundwork was already Bicep. [`bicep/files-iac.bicep`](bicep/files-iac.bicep)
and its module [`files-iac-rg.bicep`](bicep/files-iac-rg.bicep) build the
**end state** of the new part in one deployment, in `rg-lab-files-iac`:

| Portal step | Bicep | Note |
|---|---|---|
| Configuration: keys off, Entra default | `allowSharedKeyAccess: false`, `defaultToOAuthAuthentication: true` | set from birth |
| Soft delete 7 days | `fileServices` `shareDeleteRetentionPolicy` | the hidden service layer, like blob services in lab 02 |
| + File share | `shares` `branch-docs`, `TransactionOptimized` | created through ARM, so keys off does not block it |
| IAM: Privileged Reader | `roleAssignments`, role `b8eda974-7b85-4f76-af95-65846b26df6d` | object ID looked up at deploy time |

```powershell
az deployment sub create -l eastus -n lab06-files-iac -f files-iac.bicep -p principalId=$(az ad signed-in-user show --query id -o tsv) --query properties.outputs
```

![files-iac deployment](screenshots/06-33-files-iac-deploy.png)

*Figure 6.35: The end-state deployment.*

![IaC share list](screenshots/06-34-iac-share-settings.png)

*Figure 6.36: stlabfilesnoble02: branch-docs, Transaction optimized, soft delete 7 days.*

![Opened with Entra](screenshots/06-35-iac-share-entra-empty.png)

*Figure 6.37: The keys-off account opens straight into Microsoft Entra user account.*

**Result (21 Nov 2026):** deployed first time. Checked from the CLI: shared
key access False, Entra default True, the share Transaction optimized, and one
role on the account: Storage File Data Privileged Reader.

## What I found

- **SMB depends on the network, HTTPS does not.** Port 445 decides whether a
  mapped drive is possible at all; check it first.
- **A storage key is one password for every file.** SMB mounts with it log in
  as the account itself, so files cannot tell people apart.
- **Owner is not a file reader.** Without the key, Owner cannot list a share.
  Data access needs a data role.
- **The portal hides which credential it uses.** The *Authentication method*
  line is the only clue; it can switch back to the key on its own.
- **Turning keys off is immediate and total.** Good in an emergency, and a
  reason to inventory key users before doing it in production.
- **Snapshots are the cheap undo button**; Azure Backup automates them.

The sentence to keep: *check port 445, then decide who gets in by role, not by key.*

## Not covered

Identity-based SMB (per-user mounts and file permissions) needs AD DS, Entra
Domain Services or Entra Kerberos. A good follow-up with the homelab's Active
Directory.

## Cost

Well under a dollar: about two hours of a Standard_B2ats_v2 VM (about 1 cent
an hour) plus its disk and public IP, and pennies of file storage and
transactions.

## Teardown

Done 21 Nov 2026:

```powershell
az group delete --name rg-lab-files --yes --no-wait
az group delete --name rg-lab-files-iac --yes --no-wait
```

![Teardown](screenshots/06-36-teardown.png)

*Figure 6.38: Both resource groups deleted.*
