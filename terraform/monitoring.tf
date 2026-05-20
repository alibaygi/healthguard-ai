# ---------------------------------------------------------------------------
# Log Analytics Workspace — backend for Application Insights
# ---------------------------------------------------------------------------
resource "azurerm_log_analytics_workspace" "main" {
  name                = "${var.prefix}-law"
  resource_group_name = azurerm_resource_group.main.name
  location            = var.location
  sku                 = "PerGB2018"
  retention_in_days   = 30
  tags                = var.tags
}

# ---------------------------------------------------------------------------
# Application Insights — OpenTelemetry sink for FastAPI traces & metrics
# ---------------------------------------------------------------------------
resource "azurerm_application_insights" "main" {
  name                = "${var.prefix}-appinsights"
  resource_group_name = azurerm_resource_group.main.name
  location            = var.location
  workspace_id        = azurerm_log_analytics_workspace.main.id
  application_type    = "web"
  tags                = var.tags
}
