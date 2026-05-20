# ---------------------------------------------------------------------------
# Random suffix to guarantee a globally unique storage account name
# ---------------------------------------------------------------------------
resource "random_string" "storage_suffix" {
  length  = 6
  special = false
  upper   = false
}

# ---------------------------------------------------------------------------
# Storage Account — required by Azure Video Indexer for media storage
# Name constraints: 3-24 chars, lowercase letters and numbers only
# ---------------------------------------------------------------------------
resource "azurerm_storage_account" "vi" {
  name                     = "${replace(var.prefix, "-", "")}vi${random_string.storage_suffix.result}"
  resource_group_name      = azurerm_resource_group.main.name
  location                 = var.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  account_kind             = "StorageV2"
  tags                     = var.tags
}

# ---------------------------------------------------------------------------
# User-Assigned Managed Identity for Video Indexer
# Using user-assigned identity avoids the circular dependency that arises
# when a system-assigned identity needs storage access at creation time.
# ---------------------------------------------------------------------------
resource "azurerm_user_assigned_identity" "vi" {
  name                = "${var.prefix}-vi-identity"
  resource_group_name = azurerm_resource_group.main.name
  location            = var.location
  tags                = var.tags
}

# Grant the Video Indexer identity Owner rights on the storage account
# (required for Video Indexer to read/write media blobs)
resource "azurerm_role_assignment" "vi_storage_identity" {
  scope                = azurerm_storage_account.vi.id
  role_definition_name = "Storage Blob Data Owner"
  principal_id         = azurerm_user_assigned_identity.vi.principal_id
}

# ---------------------------------------------------------------------------
# Azure Video Indexer Account
# ---------------------------------------------------------------------------
resource "azurerm_video_indexer_account" "main" {
  name                = "${var.prefix}-vi"
  resource_group_name = azurerm_resource_group.main.name
  location            = var.location

  storage {
    storage_account_id        = azurerm_storage_account.vi.id
    user_assigned_identity_id = azurerm_user_assigned_identity.vi.id
  }

  identity {
    type         = "UserAssigned"
    identity_ids = [azurerm_user_assigned_identity.vi.id]
  }

  tags = var.tags

  # Ensure the identity has storage access before account creation
  depends_on = [azurerm_role_assignment.vi_storage_identity]
}
