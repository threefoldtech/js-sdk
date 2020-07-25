const WIKIS = {
  sdk: {
    title: "SDK",
    path: "/wikis/sdk",
    url: "https://sdk.threefold.io"
  },
  threefold: {
    title: "Threefold",
    path: "/wikis/threefold",
    url: "https://wiki.threefold.io"
  }
}

const SOLUTIONS = {
  ubuntu: {
    topic: "ubuntu_deploy",
    name: "Ubuntu",
    type: "ubuntu",
    image: "./assets/ubuntu.png",
    url: "/solutions/ubuntu_deploy",
    description: "A free and open-source Linux distribution based on Debian. Ubuntu is officially released in three editions: Desktop, Server, and Core(for internet of things devices and robots). This package is used to deploy an ubuntu container from an official flist on the grid using a chatflow."
  },
  kubernetes: {
    topic: "kubernetes_deploy",
    name: "Kubernetes",
    type: "kubernetes",
    image: "./assets/kubernetes.png",
    url: "/solutions/kubernetes_deploy",
    description: "Deploy a Kubernetes cluster with zdb using a chatflow. In this guide we will walk you through the provisioning of a full-blown kubernetes cluster on the TF grid. We will then see how to connect to it and interact using kubectl on our local machine. Finally we will go through some examples use cases to grasp the features offered by the cluster."
  },
  minio: {
    topic: "minio_deploy",
    type: "minio",
    name: "Minio",
    image: "./assets/minio.png",
    url: "/solutions/minio_deploy",
    description: "MinIO is a high performance object storage. With the assist of the chatflow the user will deploy a machine with MinIO along with the number of zdbs needed for storage."
  },
  gitea: {
    topic: "gitea_deploy",
    type: "gitea",
    name: "Gitea",
    image: "./assets/gitea.png",
    url: "/solutions/gitea_deploy",
    description: "Gitea is a painless self-hosted Git service. It is similar to GitHub, Bitbucket, and GitLab."
  },
  network: {
    topic: "network_deploy",
    type: "network",
    name: "Network",
    icon: "mdi-network",
    url: "/solutions/network_deploy",
    description: "Deploy a network on the grid and to connect your solutions together."
  },
  threebot: {
    topic: "threebot",
    type: "threebot",
    name: "Threebot",
    image: "./assets/3bot.png",
    url: "/solutions/threebot",
    description: "Deploy your Threebot on container."
  },
  expose: {
    topic: "solution_expose",
    type: "exposed",
    name: "Solution Expose",
    icon: "mdi-publish",
    url: "/solutions/solution_expose",
    description: ""
  },
  flist: {
    topic: "flist_deploy",
    type: "flist",
    name: "Generic Container",
    icon: "mdi-folder-multiple",
    url: "/solutions/flist_deploy",
    description: "Spawn a container using specific flist provided by the user in the chatflow."
  },
  monitoring: {
    topic: "monitoring_deploy",
    type: "monitoring",
    name:"Monitoring",
    icon: "mdi-monitor-dashboard",
    url: "/solutions/monitoring_deploy",
    description: ""
  },
  domain: {
    topic: "domain_delegation",
    type: "delegated_domain",
    name: "Domain Delegation",
    icon: "mdi-web",
    url: "/solutions/domain_delegation",
    description: ""
  },
  fourtosixgw: {
    topic: "4to6gw",
    type: "4to6gw",
    name: "4 to 6 Gateway",
    icon: "mdi-router",
    url: "/solutions/4to6gw",
    description: ""
  },
  publisher: {
    topic: "publisher",
    type: "publisher",
    name: "Publisher",
    icon: "mdi-web-box",
    url: "/solutions/publisher",
    description: ""
  },
  all: {
    topic: "all",
    type: "all_reservations",
    name:"All Reservations",
    icon: "mdi-clipboard-list-outline",
    url: "/solutions/all",
    description: ""
  }
}

const LEVELS = {
  50: { value: 50, text: "CRITICAL", color: "#A93226"},
  40: { value: 40, text: "ERROR", color: "#CB4335"},
  30: { value: 30, text: "WARNING", color: "#F39C12"},
  20: { value: 20, text: "INFO", color: "#148F77"},
  15: { value: 15, text: "STDOUT", color: "#5499C7"},
  10: { value: 10, text: "DEBUG", color: "#839192"}
};

const STATES = [
  'closed',
  'new',
  'open',
  'reopen'
]

const TYPES = [
  'bug',
  'question',
  'event_system',
  'event_monitor',
  'event_operator',
]
