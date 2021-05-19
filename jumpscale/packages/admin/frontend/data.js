const DOCS_BASE_URL = "https://wiki.threefold.io/info/sdk#"

const WIKIS = {
  sdk: {
    title: "Threefold Manual",
    path: "/wikis/sdk",
    url: "https://sdk.threefold.io"
  },
  threefold: {
    title: "Threefold Wiki",
    path: "/wikis/threefold",
    url: "https://wiki.threefold.io"
  }
}

const SOLUTIONS = {
  network: {
    name: "Network",
    type: "network",
    image: "./assets/network.png",
    url: "/solutions/network",
    helpLink: `${DOCS_BASE_URL}/sdk__solution_network`,
    description: "Deploy a network on the grid to connect your solutions together."
  },
  ubuntu: {
    name: "Ubuntu",
    type: "ubuntu",
    image: "./assets/ubuntu.png",
    url: "/solutions/ubuntu",
    helpLink: `${DOCS_BASE_URL}/sdk__solution_ubuntu`,
    description: "A free and open-source Linux distribution based on Debian. Ubuntu is officially released in three editions: Desktop, Server, and Core(for internet of things devices and robots). This package is used to deploy an ubuntu container from an official flist on the grid using a chatflow."
  },
  kubernetes: {
    name: "Kubernetes",
    type: "kubernetes",
    image: "./assets/kubernetes.png",
    url: "/solutions/kubernetes",
    helpLink: `${DOCS_BASE_URL}/sdk__solution_kubernetes`,
    description: "Deploy a Kubernetes cluster on the TF grid using a chatflow. This cluster can then be interacted with using kubectl on the user's local machine."
  },
  minio: {
    name: "S3 Storage",
    type: "minio",
    image: "./assets/minio.png",
    url: "/solutions/minio",
    helpLink: `${DOCS_BASE_URL}/sdk__solution_storage`,
    description: "S3 Storage solution uses MinIO which is a high performance object storage. With the assist of the chatflow the user will deploy a machine with MinIO along with a number of zdbs needed for storage."
  },
  expose: {
    name: "Solution Expose",
    type: "exposed",
    image: "./assets/expose.png",
    url: "/solutions/exposed",
    helpLink: `${DOCS_BASE_URL}/sdk__solution_expose`,
    description: "Access your web application running on the grid using a FQDN"
  },
  vmachine: {
    name: "Virtual Machine",
    type: "vmachine",
    image: "./assets/vmachine.png",
    url: "/solutions/vmachine",
    helpLink: ``,
    description: "Create a generic virtual machine"
  },
  flist: {
    name: "Generic Container",
    type: "flist",
    image: "./assets/flist.png",
    url: "/solutions/flist",
    helpLink: `${DOCS_BASE_URL}/sdk__solution_container`,
    description: "Spawn a container using a specific flist provided by the user in the chatflow."
  },
  monitoring: {
    name: "Monitoring",
    type: "monitoring",
    image: "./assets/monitoring.png",
    url: "/solutions/monitoring",
    helpLink: `${DOCS_BASE_URL}/sdk__monitoring`,
    description: "Deploy a basic monitoring stack (Prometheus, Grafana, Redis)"
  },
  domain: {
    name: "Domain Delegation",
    type: "delegated_domain",
    image: "./assets/web.png",
    url: "/solutions/delegated_domain",
    helpLink: `${DOCS_BASE_URL}/sdk__delegate_domain`,
    description: "Delegate your domains to our gateways"
  },
  fourtosixgw: {
    name: "4 to 6 Gateway",
    type: "gw4to6",
    image: "./assets/4to6.png",
    url: "/solutions/gw4to6",
    helpLink: `${DOCS_BASE_URL}/sdk__four_to_six_gateway`,
    description: "4to6 Gateway gives you access to IPv6 networks using a wireguard tunnel"
  },
  etcd: {
    name: "etcd",
    type: "etcd",
    image: "./assets/etcd.png",
    url: "/solutions/etcd",
    helpLink: `${DOCS_BASE_URL}/sdk__solution_etcd`,
    description: "A distributed, reliable key-value store for the most critical data of a distributed system"
  }
}


const LEVELS = {
  50: { value: 50, text: "CRITICAL", color: "#A93226" },
  40: { value: 40, text: "ERROR", color: "#CB4335" },
  30: { value: 30, text: "WARNING", color: "#F39C12" },
  20: { value: 20, text: "INFO", color: "#148F77" },
  15: { value: 15, text: "STDOUT", color: "#5499C7" },
  10: { value: 10, text: "DEBUG", color: "#839192" }
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

const VOLUMES_TYPE = {
  0: "HDD",
  1: "SSD"
}

const Workload_STATE = {
  0: "Error",
  1: "Ok",
  2: "Deleted",
}
