locals {
  azurerm_resource_group_rg_name                              = "rg-terraform-dev"
  azurerm_resource_group_rg_location                          = "westeurope"
  azurerm_kubernetes_cluster_aks_name                         = "aks-terraform-dev"
  azurerm_kubernetes_cluster_aks_dns_prefix                   = "aks-terraform-dev"
  azurerm_kubernetes_cluster_aks_default_node_pool_name       = "default"
  azurerm_kubernetes_cluster_aks_default_node_pool_node_count = 1
  azurerm_kubernetes_cluster_aks_default_node_pool_vm_size    = "Standard_B2s"
}
