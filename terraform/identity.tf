# ---------------------------------------------------------------------------
# Azure AD Application + Service Principal
# The SP is used by the Python backend to authenticate to Azure services.
# ---------------------------------------------------------------------------
resource "azuread_application" "main" {
  display_name = "${var.prefix}-app"
}

resource "azuread_service_principal" "main" {
  client_id = azuread_application.main.client_id
}

resource "azuread_service_principal_password" "main" {
  service_principal_id = azuread_service_principal.main.object_id
}

# ---------------------------------------------------------------------------
# RBAC — grant the service principal the minimum required permissions
# ---------------------------------------------------------------------------

# Azure OpenAI: call GPT-4o and embeddings
resource "azurerm_role_assignment" "sp_openai" {
  scope                = azurerm_cognitive_account.openai.id
  role_definition_name = "Cognitive Services OpenAI User"
  principal_id         = azuread_service_principal.main.object_id
}

# Azure AI Search: read and write the vector index
resource "azurerm_role_assignment" "sp_search_data" {
  scope                = azurerm_search_service.main.id
  role_definition_name = "Search Index Data Contributor"
  principal_id         = azuread_service_principal.main.object_id
}

resource "azurerm_role_assignment" "sp_search_service" {
  scope                = azurerm_search_service.main.id
  role_definition_name = "Search Service Contributor"
  principal_id         = azuread_service_principal.main.object_id
}

# Azure Video Indexer: upload and manage videos
resource "azurerm_role_assignment" "sp_vi" {
  scope                = azurerm_video_indexer_account.main.id
  role_definition_name = "Contributor"
  principal_id         = azuread_service_principal.main.object_id
}

# Azure Storage: direct blob access (needed for Video Indexer upload flow)
resource "azurerm_role_assignment" "sp_storage" {
  scope                = azurerm_storage_account.vi.id
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = azuread_service_principal.main.object_id
}
