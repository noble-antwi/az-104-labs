// The resource-group half of files-iac.bicep. Each block maps to a portal step.
param name string
param location string
param tags object
param principalId string

// Built-in role: Storage File Data Privileged Reader (same ID in every tenant).
var fileReaderRoleId = subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'b8eda974-7b85-4f76-af95-65846b26df6d')

// Portal: Configuration > key access Disabled, Entra default Enabled.
resource sa 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: name
  location: location
  tags: tags
  sku: { name: 'Standard_LRS' }
  kind: 'StorageV2'
  properties: {
    accessTier: 'Hot'
    minimumTlsVersion: 'TLS1_2'
    supportsHttpsTrafficOnly: true
    allowBlobPublicAccess: false
    allowSharedKeyAccess: false
    defaultToOAuthAuthentication: true
  }
}

// The hidden middle layer for Azure Files, where soft delete lives (7 days, as in the portal default).
resource fileSvc 'Microsoft.Storage/storageAccounts/fileServices@2023-05-01' = {
  parent: sa
  name: 'default'
  properties: {
    shareDeleteRetentionPolicy: { enabled: true, days: 7 }
  }
}

// Portal: File shares > + File share > branch-docs, Transaction optimized.
resource share 'Microsoft.Storage/storageAccounts/fileServices/shares@2023-05-01' = {
  parent: fileSvc
  name: 'branch-docs'
  properties: {
    accessTier: 'TransactionOptimized'
  }
}

// Portal: Access control (IAM) > Storage File Data Privileged Reader > you.
resource reader 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(sa.id, principalId, fileReaderRoleId)
  scope: sa
  properties: {
    roleDefinitionId: fileReaderRoleId
    principalId: principalId
    principalType: 'User'
  }
}

output shareUrl string = '${sa.properties.primaryEndpoints.file}branch-docs'
