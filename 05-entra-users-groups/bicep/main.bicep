// Lab 05 rebuilt as code: the same three groups and the same nesting, plus
// Reader for the nested group on a resource group.
//
// Groups live in Entra ID, not in Azure Resource Manager, so they come from
// the Microsoft Graph Bicep extension (see bicepconfig.json). The role
// assignment is ordinary Azure RBAC, so the deployment runs at subscription
// level to create the resource group, and a module assigns the role inside it.
//
// The six l5- users already exist (created by scripts/bulk-create-users.ps1),
// so they are looked up as `existing`, never created or stored here.
//
// Deploy:  az deployment sub create -l eastus -f main.bicep
targetScope = 'subscription'

extension microsoftGraphV1

@description('Empty resource group that receives the Reader assignment (free).')
param resourceGroupName string = 'rg-lab-entra-iac'

param location string = 'eastus'

var domain = 'biira.online'
var branchUpns = [ 'l5-amensah', 'l5-kboateng', 'l5-easante' ]
var treasuryUpns = [ 'l5-ydarko', 'l5-aowusu', 'l5-kadjei' ]

// Look up the users by UPN. Graph returns their object IDs at deploy time.
resource branchUsers 'Microsoft.Graph/users@v1.0' existing = [for u in branchUpns: {
  userPrincipalName: '${u}@${domain}'
}]

resource treasuryUsers 'Microsoft.Graph/users@v1.0' existing = [for u in treasuryUpns: {
  userPrincipalName: '${u}@${domain}'
}]

// Portal: Groups > New group > Security, Assigned, add members.
// uniqueName is the key Bicep uses to find the group again on redeploy.
resource branchOps 'Microsoft.Graph/groups@v1.0' = {
  uniqueName: 'l5-iac-branch-operations'
  displayName: 'L5-IaC-Branch-Operations'
  description: 'Lab 05 (Bicep): branch staff'
  securityEnabled: true
  mailEnabled: false
  mailNickname: 'l5-iac-branch-operations'
  members: {
    relationships: [for (u, i) in branchUpns: branchUsers[i].id]
  }
}

resource treasury 'Microsoft.Graph/groups@v1.0' = {
  uniqueName: 'l5-iac-treasury'
  displayName: 'L5-IaC-Treasury'
  description: 'Lab 05 (Bicep): treasury staff'
  securityEnabled: true
  mailEnabled: false
  mailNickname: 'l5-iac-treasury'
  members: {
    relationships: [for (u, i) in treasuryUpns: treasuryUsers[i].id]
  }
}

// The nested group: its members are the two groups, no people directly.
resource allStaff 'Microsoft.Graph/groups@v1.0' = {
  uniqueName: 'l5-iac-all-staff'
  displayName: 'L5-IaC-All-Staff'
  description: 'Lab 05 (Bicep): nested, holds both teams'
  securityEnabled: true
  mailEnabled: false
  mailNickname: 'l5-iac-all-staff'
  members: {
    relationships: [ branchOps.id, treasury.id ]
  }
}

resource rg 'Microsoft.Resources/resourceGroups@2024-03-01' = {
  name: resourceGroupName
  location: location
  tags: {
    environment: 'lab'
    purpose: 'lab'
    lab: '05-entra-users-groups'
    autoDelete: 'true'
  }
}

// Portal: rg > Access control (IAM) > Add role assignment > Reader > the group.
module reader 'reader.bicep' = {
  name: 'reader-to-all-staff'
  scope: rg
  params: {
    principalId: allStaff.id
  }
}

output allStaffGroupId string = allStaff.id
output resourceGroup string = rg.name
