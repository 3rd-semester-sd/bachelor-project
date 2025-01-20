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


  oms_agent {
    log_analytics_workspace_id = azurerm_log_analytics_workspace.aks_logging.id
  }


  identity {
    type = "SystemAssigned"
  }
}

resource "azurerm_log_analytics_workspace" "aks_logging" {
  name                = "my-aks-logs-workspace"
  location            = var.rg_location
  resource_group_name = var.rg_name
  sku                 = "PerGB2018"
  retention_in_days   = 30
}

resource "azurerm_log_analytics_solution" "container_insights" {
  solution_name         = "ContainerInsights"
  location              = azurerm_log_analytics_workspace.aks_logging.location
  resource_group_name   = var.rg_name
  workspace_resource_id = azurerm_log_analytics_workspace.aks_logging.id
  workspace_name        = azurerm_log_analytics_workspace.aks_logging.name

  plan {
    publisher = "Microsoft"
    product   = "OMSGallery/ContainerInsights"
  }
}
# resource "azurerm_monitor_diagnostic_setting" "aks" {
#   name                       = "aks-diagnostics"
#   target_resource_id         = azurerm_kubernetes_cluster.aks.id
#   log_analytics_workspace_id = azurerm_log_analytics_workspace.aks_logging.id

#   enabled_log {
#     category = "kube-apiserver"
#   }

#   enabled_log {
#     category = "kube-audit"
#   }

#   enabled_log {
#     category = "kube-controller-manager"
#   }

#   enabled_log {
#     category = "kube-scheduler"
#   }

#   enabled_log {
#     category = "cluster-autoscaler"
#   }
# }
