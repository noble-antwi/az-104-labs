// Lab 06 test client: a small Linux VM inside Azure, used only to map the
// file share over SMB. Home internet blocks port 445; Azure's network does
// not, so the mount is tested from here. Same shape as the lab 03 VM, made
// smaller, with cifs-utils (the Linux SMB client) installed at first boot.
//
// Deploy into the lab 06 resource group:
//   az deployment group create -g rg-lab-files -n lab06-vm -f vm.bicep `
//     -p adminPublicKey="$(Get-Content $HOME\.ssh\vm-lab-01.pub)" `
//        sshSourceAddress="$((Invoke-RestMethod https://api.ipify.org))/32"

param location string = resourceGroup().location

@description('SSH public key for azureuser. Read from your .pub file at deploy time, never stored here.')
param adminPublicKey string

@description('Your home public IP as a /32. Only this address may SSH in.')
param sshSourceAddress string

param vmName string = 'vm-files-01'

param adminUsername string = 'azureuser'

// B1s is no longer offered in East US; B2ats_v2 is the smallest B size (2 vCPU, 1 GiB, about 1 cent an hour).
param vmSize string = 'Standard_B2ats_v2'

var tags = {
  environment: 'lab'
  purpose: 'lab'
  lab: '06-azure-files-share'
  owner: 'noble'
  costCenter: 'it-lab'
  autoDelete: 'true'
}

// Network: one VNet, one subnet. Same pattern as lab 03, different range.
resource vnet 'Microsoft.Network/virtualNetworks@2024-01-01' = {
  name: 'vnet-lab-files'
  location: location
  tags: tags
  properties: {
    addressSpace: { addressPrefixes: [ '10.60.0.0/16' ] }
    subnets: [
      {
        name: 'snet-clients'
        properties: { addressPrefix: '10.60.0.0/24' }
      }
    ]
  }
}

// Firewall for the NIC: SSH only from your IP. Outbound (including 445 to
// Azure Files) is allowed by the default rules.
resource nsg 'Microsoft.Network/networkSecurityGroups@2024-01-01' = {
  name: '${vmName}-nsg'
  location: location
  tags: tags
  properties: {
    securityRules: [
      {
        name: 'allow-ssh-from-my-ip'
        properties: {
          priority: 100
          direction: 'Inbound'
          access: 'Allow'
          protocol: 'Tcp'
          sourceAddressPrefix: sshSourceAddress
          sourcePortRange: '*'
          destinationAddressPrefix: '*'
          destinationPortRange: '22'
        }
      }
    ]
  }
}

resource pip 'Microsoft.Network/publicIPAddresses@2024-01-01' = {
  name: '${vmName}-ip'
  location: location
  tags: tags
  sku: { name: 'Standard' }
  properties: { publicIPAllocationMethod: 'Static' }
}

resource nic 'Microsoft.Network/networkInterfaces@2024-01-01' = {
  name: '${vmName}-nic'
  location: location
  tags: tags
  properties: {
    networkSecurityGroup: { id: nsg.id }
    ipConfigurations: [
      {
        name: 'ipconfig1'
        properties: {
          subnet: { id: vnet.properties.subnets[0].id }
          privateIPAllocationMethod: 'Dynamic'
          publicIPAddress: { id: pip.id }
        }
      }
    ]
  }
}

// cloud-init runs once at first boot: install the SMB client.
var cloudInit = '''#cloud-config
package_update: true
packages:
  - cifs-utils
'''

resource vm 'Microsoft.Compute/virtualMachines@2024-07-01' = {
  name: vmName
  location: location
  tags: tags
  properties: {
    hardwareProfile: { vmSize: vmSize }
    securityProfile: {
      securityType: 'TrustedLaunch'
      uefiSettings: { secureBootEnabled: true, vTpmEnabled: true }
    }
    storageProfile: {
      imageReference: {
        publisher: 'canonical'
        offer: 'ubuntu-24_04-lts'
        sku: 'server'
        version: 'latest'
      }
      osDisk: {
        createOption: 'FromImage'
        managedDisk: { storageAccountType: 'StandardSSD_LRS' }
        deleteOption: 'Delete'
      }
    }
    osProfile: {
      computerName: vmName
      adminUsername: adminUsername
      customData: base64(cloudInit)
      linuxConfiguration: {
        disablePasswordAuthentication: true
        ssh: {
          publicKeys: [
            {
              path: '/home/${adminUsername}/.ssh/authorized_keys'
              keyData: adminPublicKey
            }
          ]
        }
      }
    }
    networkProfile: {
      networkInterfaces: [ { id: nic.id, properties: { deleteOption: 'Delete' } } ]
    }
  }
}

// Safety net: deallocate every night at 01:00 Chicago time.
resource shutdown 'Microsoft.DevTestLab/schedules@2018-09-15' = {
  name: 'shutdown-computevm-${vmName}'
  location: location
  tags: tags
  properties: {
    status: 'Enabled'
    taskType: 'ComputeVmShutdownTask'
    dailyRecurrence: { time: '0100' }
    timeZoneId: 'Central Standard Time'
    notificationSettings: { status: 'Disabled' }
    targetResourceId: vm.id
  }
}

output sshCommand string = 'ssh -i $HOME\\.ssh\\vm-lab-01 ${adminUsername}@${pip.properties.ipAddress}'
