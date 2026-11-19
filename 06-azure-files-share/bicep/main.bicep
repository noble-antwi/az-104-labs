// Lab 06 starting point, built as code because it repeats lab 02:
// a resource group and a plain StorageV2 account. The file share itself is
// built by hand in the portal, because that is what this lab is about.
//
// Deploy:  az deployment sub create -l eastus -n lab06-base -f main.bicep
targetScope = 'subscription'

param location string = 'eastus'
param resourceGroupName string = 'rg-lab-files'
param storageAccountName string = 'stlabfilesnoble01'

var tags = {
  environment: 'lab'
  purpose: 'lab'
  lab: '06-azure-files-share'
  owner: 'noble'
  costCenter: 'it-lab'
  autoDelete: 'true'
}

resource rg 'Microsoft.Resources/resourceGroups@2024-03-01' = {
  name: resourceGroupName
  location: location
  tags: tags
}

module storage 'storage.bicep' = {
  name: 'storage'
  scope: rg
  params: {
    name: storageAccountName
    location: location
    tags: tags
  }
}

output storageAccount string = storage.outputs.name
output fileEndpoint string = storage.outputs.fileEndpoint
