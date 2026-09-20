// Data Estate Modernization - landing zone starter
// Deploys: (1) a Fabric capacity, (2) an Azure SQL logical server with Entra-only admin.
// Verify current API versions, SKUs and quota against Microsoft Learn before production use.

@description('Azure region for all resources')
param location string = resourceGroup().location

@description('Name of the Fabric capacity resource')
param fabricCapacityName string

@description('Fabric capacity SKU (e.g. F2, F4, F8, F16, F32, F64...)')
param fabricSku string = 'F8'

@description('UPNs or object IDs of Fabric capacity administrators')
param fabricAdmins array

@description('Name of the Azure SQL logical server')
param sqlServerName string

@description('Display name of the Entra ID group used as SQL admin (Entra-only auth)')
param sqlAdminGroupName string

@description('Object ID of the Entra ID group used as SQL admin')
param sqlAdminGroupObjectId string

resource fabricCapacity 'Microsoft.Fabric/capacities@2023-11-01' = {
  name: fabricCapacityName
  location: location
  sku: {
    name: fabricSku
    tier: 'Fabric'
  }
  properties: {
    administration: {
      members: fabricAdmins
    }
  }
}

resource sqlServer 'Microsoft.Sql/servers@2023-08-01-preview' = {
  name: sqlServerName
  location: location
  properties: {
    minimalTlsVersion: '1.2'
    publicNetworkAccess: 'Disabled'
    administrators: {
      administratorType: 'ActiveDirectory'
      principalType: 'Group'
      login: sqlAdminGroupName
      sid: sqlAdminGroupObjectId
      azureADOnlyAuthentication: true
    }
  }
}

output fabricCapacityId string = fabricCapacity.id
output sqlServerId string = sqlServer.id
output sqlServerFqdn string = sqlServer.properties.fullyQualifiedDomainName
