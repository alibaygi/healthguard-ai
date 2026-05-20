# ---------------------------------------------------------------------------
# Azure AI Search — Standard SKU required for vector search (RAG)
# ---------------------------------------------------------------------------
resource "azurerm_search_service" "main" {
  name                = "${var.prefix}-search"
  resource_group_name = azurerm_resource_group.main.name
  location            = var.location
  sku                 = var.search_sku
  tags                = var.tags
}
