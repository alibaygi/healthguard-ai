# ---------------------------------------------------------------------------
# Run `terraform output -json` to see sensitive values (API keys, secrets).
# Each output name maps directly to its .env variable name.
# ---------------------------------------------------------------------------

output "AZURE_SUBSCRIPTION_ID" {
  description = "Azure Subscription ID"
  value       = var.subscription_id
}

output "AZURE_TENANT_ID" {
  description = "Azure AD Tenant ID"
  value       = data.azurerm_subscription.current.tenant_id
}

output "AZURE_CLIENT_ID" {
  description = "Service Principal client (application) ID"
  value       = azuread_application.main.client_id
}

output "AZURE_CLIENT_SECRET" {
  description = "Service Principal client secret — store securely"
  value       = azuread_service_principal_password.main.value
  sensitive   = true
}

output "AZURE_RESOURCE_GROUP" {
  description = "Resource Group name"
  value       = azurerm_resource_group.main.name
}

# ---------------------------------------------------------------------------
# Azure OpenAI
# ---------------------------------------------------------------------------
output "AZURE_OPENAI_ENDPOINT" {
  description = "Azure OpenAI endpoint URL"
  value       = azurerm_cognitive_account.openai.endpoint
}

output "AZURE_OPENAI_API_KEY" {
  description = "Azure OpenAI primary API key"
  value       = azurerm_cognitive_account.openai.primary_access_key
  sensitive   = true
}

output "AZURE_OPENAI_CHAT_DEPLOYMENT" {
  description = "GPT-4o deployment name"
  value       = azurerm_cognitive_deployment.gpt4o.name
}

output "AZURE_OPENAI_EMBEDDING_DEPLOYMENT" {
  description = "text-embedding-3-small deployment name"
  value       = azurerm_cognitive_deployment.embedding.name
}

output "AZURE_OPENAI_API_VERSION" {
  description = "Recommended OpenAI REST API version"
  value       = "2024-10-01-preview"
}

# ---------------------------------------------------------------------------
# Azure AI Search
# ---------------------------------------------------------------------------
output "AZURE_SEARCH_ENDPOINT" {
  description = "Azure AI Search endpoint URL"
  value       = "https://${azurerm_search_service.main.name}.search.windows.net"
}

output "AZURE_SEARCH_API_KEY" {
  description = "Azure AI Search primary admin key"
  value       = azurerm_search_service.main.primary_key
  sensitive   = true
}

# ---------------------------------------------------------------------------
# Azure Video Indexer
# ---------------------------------------------------------------------------
output "AZURE_VI_NAME" {
  description = "Video Indexer account name"
  value       = azurerm_video_indexer_account.main.name
}

output "AZURE_VI_LOCATION" {
  description = "Video Indexer account location"
  value       = azurerm_video_indexer_account.main.location
}

output "AZURE_VI_ACCOUNT_ID" {
  description = "Video Indexer account GUID (used in API calls)"
  value       = azurerm_video_indexer_account.main.account_id
}

# ---------------------------------------------------------------------------
# Azure Storage
# ---------------------------------------------------------------------------
output "AZURE_STORAGE_CONNECTION_STRING" {
  description = "Storage Account primary connection string"
  value       = azurerm_storage_account.vi.primary_connection_string
  sensitive   = true
}

# ---------------------------------------------------------------------------
# Azure Monitor
# ---------------------------------------------------------------------------
output "APPLICATIONINSIGHTS_CONNECTION_STRING" {
  description = "Application Insights connection string for OpenTelemetry"
  value       = azurerm_application_insights.main.connection_string
  sensitive   = true
}

# ---------------------------------------------------------------------------
# Convenience: print the full .env block (run: terraform output -raw dot_env)
# ---------------------------------------------------------------------------
output "dot_env" {
  description = "Paste this block into your .env file (terraform output -raw dot_env)"
  sensitive   = true
  value       = <<-ENV
    AZURE_TENANT_ID=${data.azurerm_subscription.current.tenant_id}
    AZURE_CLIENT_ID=${azuread_application.main.client_id}
    AZURE_SUBSCRIPTION_ID=${var.subscription_id}
    AZURE_RESOURCE_GROUP=${azurerm_resource_group.main.name}
    AZURE_OPENAI_ENDPOINT=${azurerm_cognitive_account.openai.endpoint}
    AZURE_OPENAI_API_KEY=${azurerm_cognitive_account.openai.primary_access_key}
    AZURE_OPENAI_API_VERSION=2024-10-01-preview
    AZURE_OPENAI_CHAT_DEPLOYMENT=${azurerm_cognitive_deployment.gpt4o.name}
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT=${azurerm_cognitive_deployment.embedding.name}
    AZURE_SEARCH_ENDPOINT=https://${azurerm_search_service.main.name}.search.windows.net
    AZURE_SEARCH_API_KEY=${azurerm_search_service.main.primary_key}
    AZURE_SEARCH_INDEX_NAME=health-guidelines
    AZURE_VI_NAME=${azurerm_video_indexer_account.main.name}
    AZURE_VI_LOCATION=${azurerm_video_indexer_account.main.location}
    AZURE_VI_ACCOUNT_ID=${azurerm_video_indexer_account.main.account_id}
    AZURE_STORAGE_CONNECTION_STRING=${azurerm_storage_account.vi.primary_connection_string}
    APPLICATIONINSIGHTS_CONNECTION_STRING=${azurerm_application_insights.main.connection_string}
    AZURE_CLIENT_SECRET=${azuread_service_principal_password.main.value}
  ENV
}
