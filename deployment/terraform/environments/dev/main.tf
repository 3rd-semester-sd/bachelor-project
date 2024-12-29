module "rg" {
  source      = "../../modules/azure/rg"
  rg_name     = local.azurerm_resource_group_rg_name
  rg_location = local.azurerm_resource_group_rg_location
}

module "aks" {
  depends_on = [module.rg]

  source         = "../../modules/azure/aks"
  cluster_name   = local.azurerm_kubernetes_cluster_aks_name
  rg_name        = local.azurerm_resource_group_rg_name
  rg_location    = local.azurerm_resource_group_rg_location
  dns_prefix     = local.azurerm_kubernetes_cluster_aks_dns_prefix
  dnp_name       = local.azurerm_kubernetes_cluster_aks_default_node_pool_name
  dnp_node_count = local.azurerm_kubernetes_cluster_aks_default_node_pool_node_count
  dnp_vm_size    = local.azurerm_kubernetes_cluster_aks_default_node_pool_vm_size
}
