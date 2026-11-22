// Lab 06 rebuilt as code: the new part of the lab, end state only.
// A storage account with shared key access OFF and Entra as the portal
// default, the branch-docs share with 7-day soft delete, and Storage File
// Data Privileged Reader for one person. Deployed to its own resource group.
//
// Deploy:
//   az deployment sub create -l eastus -n lab06-files-iac -f files-iac.bicep `
//     -p principalId=$(az ad signed-in-user show --query id -o tsv)
targetScope = 'subscription'

param location string = 'eastus'
param resourceGroupName string = 'rg-lab-files-iac'
param storageAccountName string = 'stlabfilesnoble02'

@description('Object ID of the person who gets read access to the files. Looked up at deploy time, never stored.')
param principalId string

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

module files 'files-iac-rg.bicep' = {
  name: 'files'
  scope: rg
  params: {
    name: storageAccountName
    location: location
    tags: tags
    principalId: principalId
  }
}

output share string = files.outputs.shareUrl
