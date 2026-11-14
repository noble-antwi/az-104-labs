// Assigns a role to one user at the scope of the resource group this module
// is deployed to. Called from main.bicep.
targetScope = 'resourceGroup'

param roleDefinitionId string
param principalId string

resource assignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(resourceGroup().id, principalId, roleDefinitionId)
  properties: {
    roleDefinitionId: roleDefinitionId
    principalId: principalId
    principalType: 'User'
  }
}
