module "rg" {
  source      = "../../modules/azure/rg"
  rg_name     = local.azurerm_resource_group_rg_name
  rg_location = local.azurerm_resource_group_rg_location
}

module "aks" {
  depends_on = [module.rg]

  source      = "../../modules/azure/aks"
  rg_name     = local.azurerm_resource_group_rg_name
  rg_location = local.azurerm_resource_group_rg_location

  cluster_name   = local.azurerm_kubernetes_cluster_aks_name
  dns_prefix     = local.azurerm_kubernetes_cluster_aks_dns_prefix
  dnp_name       = local.azurerm_kubernetes_cluster_aks_default_node_pool_name
  dnp_node_count = local.azurerm_kubernetes_cluster_aks_default_node_pool_node_count
  dnp_vm_size    = local.azurerm_kubernetes_cluster_aks_default_node_pool_vm_size
}

module "postgres-auth" {
  depends_on = [module.rg]

  source      = "../../modules/azure/postgres"
  rg_name     = local.azurerm_resource_group_rg_name
  rg_location = local.azurerm_resource_group_rg_location

  primary_server_name = local.auth_service_postgresql_primary_server_name
  admin_login         = local.auth_service_postgresql_admin_login
  admin_password      = local.auth_service_postgresql_admin_password
  sku_name            = local.auth_service_postgresql_sku_name
  firewall_rule_name  = local.auth_service_postgresql_firewall_rule_name
  database_name       = local.auth_service_database_name
  create_replica      = local.auth_service_create_replica
  create_database     = local.auth_service_create_database
}

module "postgres-booking" {
  depends_on = [module.rg]

  source      = "../../modules/azure/postgres"
  rg_name     = local.azurerm_resource_group_rg_name
  rg_location = local.azurerm_resource_group_rg_location

  primary_server_name = local.booking_service_postgresql_primary_server_name
  admin_login         = local.booking_service_postgresql_admin_login
  admin_password      = local.booking_service_postgresql_admin_password
  sku_name            = local.booking_service_postgresql_sku_name
  firewall_rule_name  = local.booking_service_postgresql_firewall_rule_name
  database_name       = local.booking_service_database_name
  create_replica      = local.booking_service_create_replica
  create_database     = local.booking_service_create_database
}

module "postgres-restaurant" {
  depends_on = [module.rg]

  source      = "../../modules/azure/postgres"
  rg_name     = local.azurerm_resource_group_rg_name
  rg_location = local.azurerm_resource_group_rg_location

  primary_server_name = local.restaurant_service_postgresql_primary_server_name
  admin_login         = local.restaurant_service_postgresql_admin_login
  admin_password      = local.restaurant_service_postgresql_admin_password
  sku_name            = local.restaurant_service_postgresql_sku_name
  firewall_rule_name  = local.restaurant_service_postgresql_firewall_rule_name
  database_name       = local.restaurant_service_database_name
  create_replica      = local.restaurant_service_create_replica
  create_database     = local.restaurant_service_create_database
}

resource "postgresql_exten"
