locals {
  # Resource Group
  azurerm_resource_group_rg_name     = "rg-terraform-dev"
  azurerm_resource_group_rg_location = "westeurope"

  # AKS
  azurerm_kubernetes_cluster_aks_name                         = "aks-terraform-dev"
  azurerm_kubernetes_cluster_aks_dns_prefix                   = "aks-terraform-dev"
  azurerm_kubernetes_cluster_aks_default_node_pool_name       = "default"
  azurerm_kubernetes_cluster_aks_default_node_pool_node_count = 2
  azurerm_kubernetes_cluster_aks_default_node_pool_vm_size    = "Standard_A4_v2"

  # PostgreSQL Auth Service
  auth_service_postgresql_primary_server_name = "pg-kea-bachelor-auth"
  auth_service_postgresql_admin_login         = "bachelor"
  auth_service_postgresql_admin_password      = "P@ssw0rd"
  auth_service_postgresql_sku_name            = "B_Gen5_2"
  auth_service_postgresql_firewall_rule_name  = "firewall-rule-kea-bachelor-auth"
  auth_service_database_name                  = "auth-db"
  auth_service_create_replica                 = true
  auth_service_create_database                = true

  # PostgreSQL Auth Service
  booking_service_postgresql_primary_server_name = "pg-kea-bachelor-booking"
  booking_service_postgresql_admin_login         = "bachelor"
  booking_service_postgresql_admin_password      = "P@ssw0rd"
  booking_service_postgresql_sku_name            = "B_Gen5_2"
  booking_service_postgresql_firewall_rule_name  = "firewall-rule-kea-bachelor-booking"
  booking_service_database_name                  = "booking-db"
  booking_service_create_replica                 = false
  booking_service_create_database                = true

  # PostgreSQL Restaurant Service
  restaurant_service_postgresql_primary_server_name = "pg-kea-bachelor-restaurant"
  restaurant_service_postgresql_admin_login         = "bachelor"
  restaurant_service_postgresql_admin_password      = "P@ssw0rd"
  restaurant_service_postgresql_sku_name            = "B_Gen5_2"
  restaurant_service_postgresql_firewall_rule_name  = "firewall-rule-kea-bachelor-restaurant"
  restaurant_service_database_name                  = "restaurant-db"
  restaurant_service_create_replica                 = false
  restaurant_service_create_database                = true
}
