// Gives a group the built-in Reader role on the resource group this module
// is deployed to. Called from main.bicep.
targetScope = 'resourceGroup'

param principalId string

// Reader's fixed built-in role ID, the same in every tenant.
var readerRoleId = subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'acdd72a7-3385-48ef-bd42-f606fba81ae7')

resource assignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(resourceGroup().id, principalId, readerRoleId)
  properties: {
    roleDefinitionId: readerRoleId
    principalId: principalId
    principalType: 'Group'
  }
}
