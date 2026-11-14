// Lab 04 custom RBAC role, rebuilt as code.
// A role definition lives at subscription level, so this file deploys to the
// subscription and hands the assignment to a module scoped to one group.
// Named "(IaC)" so it can sit beside the portal-built role while both exist:
// role names must be unique in a tenant.
targetScope = 'subscription'

@description('Object ID of the user who gets the role. Passed at deploy time, never stored.')
param principalId string

@description('The one resource group where the role is assigned.')
param resourceGroupName string = 'rg-lab-vm'

// Five actions: read the VM, start, stop (deallocate), restart, power off.
// No write, no delete, no wildcard; nothing on NICs, IPs or networks.
var vmOperatorActions = [
  'Microsoft.Compute/virtualMachines/read'
  'Microsoft.Compute/virtualMachines/start/action'
  'Microsoft.Compute/virtualMachines/deallocate/action'
  'Microsoft.Compute/virtualMachines/restart/action'
  'Microsoft.Compute/virtualMachines/powerOff/action'
]

// 1. The role definition (portal Basics, Permissions, Assignable scopes).
//    Its name must be a GUID; guid() makes the same one on every deploy.
resource vmOperator 'Microsoft.Authorization/roleDefinitions@2022-04-01' = {
  name: guid(subscription().id, 'lab-vm-operator-iac')
  properties: {
    roleName: 'Lab VM Operator (IaC)'
    description: 'Start, stop and restart VMs. Cannot create, resize or delete.'
    type: 'CustomRole'
    permissions: [
      {
        actions: vmOperatorActions
        notActions: []
        dataActions: []
        notDataActions: []
      }
    ]
    // where the role may be handed out (the menu)...
    assignableScopes: [
      subscription().id
    ]
  }
}

// 2. ...and where it is actually handed out: one resource group only.
module assignment 'assign.bicep' = {
  name: 'lab-vm-operator-assignment'
  scope: resourceGroup(resourceGroupName)
  params: {
    roleDefinitionId: vmOperator.id
    principalId: principalId
  }
}

output roleName string = vmOperator.properties.roleName
output assignedAt string = resourceGroupName
