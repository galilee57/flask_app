// Provision only a dedicated staging environment. Database is provisioned separately.
param location string = resourceGroup().location
param registryName string
param appName string = 'portfolio-staging'
param environmentName string = 'portfolio-staging-env'
param imageTag string
@secure()
param databaseUrl string
@secure()
param secretKey string
@secure()
param adminApiToken string

resource registry 'Microsoft.ContainerRegistry/registries@2023-07-01' = {
  name: registryName
  location: location
  sku: { name: 'Basic' }
  properties: { adminUserEnabled: false }
}
resource identity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: '${appName}-pull'
  location: location
}
resource pull 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(registry.id, identity.id, 'AcrPull')
  scope: registry
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '7f951dda-4ed3-4680-a7ca-43fe172d538d')
    principalId: identity.properties.principalId
    principalType: 'ServicePrincipal'
  }
}
resource environment 'Microsoft.App/managedEnvironments@2024-03-01' = {
  name: environmentName
  location: location
  properties: {}
}
var image = '${registry.properties.loginServer}/portfolio:${imageTag}'
var secrets = [
  { name: 'database-url', value: databaseUrl }
  { name: 'secret-key', value: secretKey }
  { name: 'admin-token', value: adminApiToken }
]
var variables = [
  { name: 'DATABASE_URL', secretRef: 'database-url' }
  { name: 'SECRET_KEY', secretRef: 'secret-key' }
  { name: 'ADMIN_API_TOKEN', secretRef: 'admin-token' }
  { name: 'FLASK_CONFIG', value: 'production' }
  { name: 'CONTAINER_MODE', value: 'true' }
  { name: 'PORT', value: '8080' }
]
var registries = [
  { server: registry.properties.loginServer, identity: identity.id }
]
resource app 'Microsoft.App/containerApps@2024-03-01' = {
  name: appName
  location: location
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: { '${identity.id}': {} }
  }
  properties: {
    managedEnvironmentId: environment.id
    configuration: {
      activeRevisionsMode: 'Single'
      secrets: secrets
      registries: registries
      ingress: { external: true, targetPort: 8080, transport: 'http', allowInsecure: false }
    }
    template: {
      containers: [
        {
          name: 'portfolio'
          image: image
          env: variables
          resources: { cpu: json('0.5'), memory: '1Gi' }
          probes: [
            { type: 'Startup', httpGet: { path: '/health/live', port: 8080 }, initialDelaySeconds: 5, periodSeconds: 5, failureThreshold: 30 }
            { type: 'Liveness', httpGet: { path: '/health/live', port: 8080 }, periodSeconds: 30 }
            { type: 'Readiness', httpGet: { path: '/health/ready', port: 8080 }, periodSeconds: 10 }
          ]
        }
      ]
      scale: { minReplicas: 1, maxReplicas: 3 }
    }
  }
  dependsOn: [pull]
}
resource migration 'Microsoft.App/jobs@2024-03-01' = {
  name: '${appName}-migrate'
  location: location
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: { '${identity.id}': {} }
  }
  properties: {
    environmentId: environment.id
    configuration: {
      triggerType: 'Manual'
      replicaTimeout: 600
      replicaRetryLimit: 0
      manualTriggerConfig: { parallelism: 1, replicaCompletionCount: 1 }
      secrets: secrets
      registries: registries
    }
    template: {
      containers: [
        {
          name: 'migration'
          image: image
          command: ['flask', '--app', 'wsgi', 'db', 'upgrade']
          env: variables
          resources: { cpu: json('0.5'), memory: '1Gi' }
        }
      ]
    }
  }
  dependsOn: [pull]
}
output registryLoginServer string = registry.properties.loginServer
output migrationJobName string = migration.name
output appUrl string = 'https://${app.properties.configuration.ingress.fqdn}'
