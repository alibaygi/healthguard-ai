# ---------------------------------------------------------------------------
# Azure OpenAI account
# ---------------------------------------------------------------------------
resource "azurerm_cognitive_account" "openai" {
  name                = "${var.prefix}-openai"
  resource_group_name = azurerm_resource_group.main.name
  location            = var.location
  kind                = "OpenAI"
  sku_name            = "S0"
  tags                = var.tags
}

# ---------------------------------------------------------------------------
# GPT-4o deployment (GlobalStandard for higher throughput limits)
# ---------------------------------------------------------------------------
resource "azurerm_cognitive_deployment" "gpt4o" {
  name                 = "gpt-4o"
  cognitive_account_id = azurerm_cognitive_account.openai.id

  model {
    format  = "OpenAI"
    name    = "gpt-4o"
    version = "2024-11-20"
  }

  sku {
    name     = "GlobalStandard"
    capacity = var.openai_gpt4o_capacity
  }
}

# ---------------------------------------------------------------------------
# text-embedding-3-small deployment (used for RAG vector embeddings)
# ---------------------------------------------------------------------------
resource "azurerm_cognitive_deployment" "embedding" {
  name                 = "text-embedding-3-small"
  cognitive_account_id = azurerm_cognitive_account.openai.id

  model {
    format  = "OpenAI"
    name    = "text-embedding-3-small"
    version = "1"
  }

  sku {
    name     = "Standard"
    capacity = var.openai_embedding_capacity
  }
}
