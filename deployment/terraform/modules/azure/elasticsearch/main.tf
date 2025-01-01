resource "azurerm_elastic_cloud_elasticsearch" "es" {
  name                = var.elasticsearch_name
  resource_group_name = var.rg_name
  location            = var.rg_location

  sku_name = var.sku_name

  elastic_cloud_email_address = var.elastic_cloud_email_address
  monitoring_enabled          = false
}

