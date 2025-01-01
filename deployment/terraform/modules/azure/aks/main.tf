resource "azurerm_kubernetes_cluster" "aks" {
  name                = var.cluster_name
  location            = var.rg_location
  resource_group_name = var.rg_name
  dns_prefix          = var.dns_prefix

  default_node_pool {
    name       = var.dnp_name
    node_count = var.dnp_node_count
    vm_size    = var.dnp_vm_size
  }

  identity {
    type = "SystemAssigned"
  }
}
