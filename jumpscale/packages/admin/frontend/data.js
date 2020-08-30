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
  network: {
    name: "Network",
    type: "network",
    image: "./assets/network.png",
    url: "/solutions/network",
    description: "Deploy a network on the grid to connect your solutions together."
  },
  ubuntu: {
    name: "Ubuntu",
    type: "ubuntu",
    image: "./assets/ubuntu.png",
    url: "/solutions/ubuntu",
    description: "A free and open-source Linux distribution based on Debian. Ubuntu is officially released in three editions: Desktop, Server, and Core(for internet of things devices and robots). This package is used to deploy an ubuntu container from an official flist on the grid using a chatflow."
  },
  kubernetes: {
    name: "Kubernetes",
    type: "kubernetes",
    image: "./assets/kubernetes.png",
    url: "/solutions/kubernetes",
    description: "Deploy a Kubernetes cluster using a chatflow. In this guide we will walk you through the provisioning of a full-blown kubernetes cluster on the TF grid. We will then see how to connect to it and interact using kubectl on our local machine. Finally we will go through some examples use cases to grasp the features offered by the cluster."
  },
  minio: {
    name: "S3 Storage",
    type: "minio",
    image: "./assets/minio.png",
    url: "/solutions/minio",
    description: "MinIO is a high performance object storage. With the assist of the chatflow the user will deploy a machine with MinIO along with the number of zdbs needed for storage."
  },
  gitea: {
    name: "Gitea",
    type: "gitea",
    image: "./assets/gitea.png",
    url: "/solutions/gitea",
    description: "Gitea is a painless self-hosted Git service. It is similar to GitHub, Bitbucket, and GitLab."
  },
  expose: {
    name: "Solution Expose",
    type: "exposed",
    image: "./assets/expose.png",
    url: "/solutions/exposed",
    description: "Access your web application running on the grid using a FQDN"
  },
  flist: {
    name: "Generic Container",
    type: "flist",
    image: "./assets/flist.png",
    url: "/solutions/flist",
    description: "Spawn a container using specific flist provided by the user in the chatflow."
  },
  monitoring: {
    name: "Monitoring",
    type: "monitoring",
    image: "./assets/monitoring.png",
    url: "/solutions/monitoring",
    description: "Deploy basic monitoring stack (Prometheus, Grafana, Redis)"
  },
  domain: {
    name: "Domain Delegation",
    type: "delegated_domain",
    image: "./assets/web.png",
    url: "/solutions/delegated_domain",
    description: "Delegate your domains to our gateways"
  },
  fourtosixgw: {
    name: "4 to 6 Gateway",
    type: "4to6gw",
    image: "./assets/4to6.png",
    url: "/solutions/4to6gw",
    description: "4to6 Gateway gives you access to IPv6 networks using a wireguard tunnel"
  },
}


const APPS = {
  wiki: {
    name: "Wiki",
    type: "wiki",
    image: "./assets/doc-flat.svg",
    url: "/solutions/wiki",
    description: "Publish a wiki like https://wiki.threefold.io/"
  },
  website: {
    name: "Website",
    type: "website",
    image: "./assets/web.png",
    url: "/solutions/website",
    description: "Publish a website like https://www.threefold.io/"
  },
  blog: {
    name: "Blog",
    type: "blog",
    image: "./assets/blog.png",
    url: "/solutions/blog",
    description: "Publish a blog like https://blog.threefold.io/"
  },
  mattermost: {
    name: "Mattermost",
    type: "mattermost",
    image: "./assets/mattermost.png",
    url: "/solutions/mattermost",
    description: "Mattermost is a flexible, open source messaging platform that enables secure team collaboration"
  },
  peertube: {
    name: "Peertube",
    type: "peertube",
    image: "./assets/peertube.png",
    url: "/solutions/peertube",
    description: "Peertube is a free and open-source, decentralized video platform that uses P2P technology to reduce load on individual servers."
  },
  discourse: {
    name: "Discourse",
    type: "discourse",
    image: "./assets/discourse.png",
    url: "/solutions/discourse",
    description: "Discourse is an open source Internet forum and mailing list management software application."
  },
  cryptpad: {
    name: "Cryptpad",
    type: "cryptpad",
    image: "./assets/cryptpad.png",
    url: "/solutions/cryptpad",
    description: "CryptPad is the Zero Knowledge realtime collaborative editor."
  },
  taiga: {
    name: "Taiga",
    type: "taiga",
    image: "./assets/taiga.png",
    url: "/solutions/taiga",
    description: "Taiga is the project management tool for multi-functional agile teams. Build your 'All in one' Taiga solution"
  },
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
