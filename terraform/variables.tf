variable "subscription_id" {
  description = "Azure Subscription ID — run `az account show --query id -o tsv` to find yours."
  type        = string
}

variable "prefix" {
  description = "Short name prefix applied to every resource (e.g. healthguard). Keep under 12 characters."
  type        = string
  default     = "healthguard"
}

variable "location" {
  description = "Azure region. GPT-4o is available in: eastus, swedencentral, westus, northcentralus."
  type        = string
  default     = "eastus"
}

variable "openai_gpt4o_capacity" {
  description = "GPT-4o deployment capacity (1 unit = 1,000 tokens-per-minute)."
  type        = number
  default     = 10
}

variable "openai_embedding_capacity" {
  description = "text-embedding-3-small capacity (1 unit = 1,000 tokens-per-minute)."
  type        = number
  default     = 5
}

variable "search_sku" {
  description = "Azure AI Search SKU. Must be 'standard' or higher for vector search support."
  type        = string
  default     = "standard"
}

variable "tags" {
  description = "Resource tags applied to all Azure resources."
  type        = map(string)
  default = {
    project     = "healthguard-ai"
    environment = "dev"
    managed_by  = "terraform"
  }
}
