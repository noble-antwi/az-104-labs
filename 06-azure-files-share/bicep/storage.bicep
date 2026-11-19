// The storage account for lab 06. Same safe defaults as lab 02, with one
// difference: shared key access stays ON for now, because a home PC that is
// not joined to a domain can only mount an SMB share with the account key.
// Turning keys off is a test later in the lab.
param name string
param location string
param tags object

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
    allowSharedKeyAccess: true
  }
}

output name string = sa.name
output fileEndpoint string = sa.properties.primaryEndpoints.file
