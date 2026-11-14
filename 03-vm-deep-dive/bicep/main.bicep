// Lab 03 VM deep dive, rebuilt as code.
// The same seven resources the portal made, plus the SSH rule from step 9.
// Secrets and personal addresses are parameters passed at deploy time,
// never stored in the repo.

@description('Region. Defaults to the resource group region.')
param location string = resourceGroup().location

@description('VM size. D2s_v3 has a 16 GiB temporary disk, which question 3 needs.')
param vmSize string = 'Standard_D2s_v3'

param adminUsername string = 'azureuser'

@description('Contents of the .pub file (ed25519). The public half only.')
param sshPublicKey string

@description('The one address allowed to SSH in, e.g. 203.0.113.10/32.')
param sshSourceAddress string

var vmName = 'vm-lab-01'
var tags = {
  environment: 'lab'
  purpose: 'lab'
  lab: 'vm-deep-dive'
  owner: 'noble'
  costCenter: 'it-lab'
  autoDelete: 'true'
}

// 1. The network: one VNet, one subnet
resource vnet 'Microsoft.Network/virtualNetworks@2023-11-01' = {
  name: 'vnet-lab-vm'
  location: location
  tags: tags
  properties: {
    addressSpace: { addressPrefixes: [ '10.30.0.0/16' ] }
    subnets: [
      {
        name: 'snet-eastus-1'
        properties: { addressPrefix: '10.30.0.0/24' }
      }
    ]
  }
}

// 2. The guard: defaults deny inbound; one rule lets SSH in from one address
resource nsg 'Microsoft.Network/networkSecurityGroups@2023-11-01' = {
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

// 3. The address: Standard, static, billed whether the VM runs or not
resource pip 'Microsoft.Network/publicIPAddresses@2023-11-01' = {
  name: '${vmName}-ip'
  location: location
  tags: tags
  sku: { name: 'Standard' }
  properties: {
    publicIPAllocationMethod: 'Static'
  }
}

// 4. The NIC: owns the private IP, joins subnet, NSG and public IP together
resource nic 'Microsoft.Network/networkInterfaces@2023-11-01' = {
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

// 5. The VM itself; the OS disk is created inline and deleted with the VM
resource vm 'Microsoft.Compute/virtualMachines@2024-03-01' = {
  name: vmName
  location: location
  tags: tags
  properties: {
    hardwareProfile: { vmSize: vmSize }
    storageProfile: {
      imageReference: {
        publisher: 'canonical'
        offer: 'ubuntu-24_04-lts'
        sku: 'server'
        version: 'latest'
      }
      osDisk: {
        createOption: 'FromImage'
        caching: 'ReadWrite'
        deleteOption: 'Delete'
        managedDisk: { storageAccountType: 'StandardSSD_LRS' }
      }
    }
    osProfile: {
      computerName: vmName
      adminUsername: adminUsername
      linuxConfiguration: {
        disablePasswordAuthentication: true
        ssh: {
          publicKeys: [
            {
              path: '/home/${adminUsername}/.ssh/authorized_keys'
              keyData: sshPublicKey
            }
          ]
        }
      }
    }
    networkProfile: {
      networkInterfaces: [
        { id: nic.id }
      ]
    }
    securityProfile: {
      securityType: 'TrustedLaunch'
      uefiSettings: {
        secureBootEnabled: true
        vTpmEnabled: true
      }
    }
    diagnosticsProfile: {
      bootDiagnostics: { enabled: true }
    }
  }
}

// 6. The safety net: deallocate daily at 01:00 Central time
//    The name format is fixed: the portal's Auto-shutdown page looks for it.
resource shutdown 'Microsoft.DevTestLab/schedules@2018-09-15' = {
  name: 'shutdown-computevm-${vmName}'
  location: location
  tags: tags
  properties: {
    status: 'Enabled'
    taskType: 'ComputeVmShutdownTask'
    dailyRecurrence: { time: '0100' }
    timeZoneId: 'Central Standard Time'
    targetResourceId: vm.id
    notificationSettings: { status: 'Disabled' }
  }
}

output publicIp string = pip.properties.ipAddress
output sshCommand string = 'ssh -i $HOME\\.ssh\\vm-lab-01 ${adminUsername}@${pip.properties.ipAddress}'
