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
    image: "./assets/network.png",
    url: "/solutions/network_deploy",
    description: "Deploy a network on the grid to connect your solutions together."
  },
  threebot: {
    topic: "threebot",
    type: "threebot",
    name: "3Bot",
    image: "./assets/3bot.png",
    url: "/solutions/threebot",
    description: "Deploy your 3Bot on container."
  },
  expose: {
    topic: "solution_expose",
    type: "exposed",
    name: "Solution Expose",
    image: "./assets/expose.png",
    url: "/solutions/solution_expose",
    description: "Access your web application running on the grid using a FQDN"
  },
  flist: {
    topic: "flist_deploy",
    type: "flist",
    name: "Generic Container",
    image: "./assets/flist.png",
    url: "/solutions/flist_deploy",
    description: "Spawn a container using specific flist provided by the user in the chatflow."
  },
  monitoring: {
    topic: "monitoring_deploy",
    type: "monitoring",
    name: "Monitoring",
    image: "./assets/monitoring.png",
    url: "/solutions/monitoring_deploy",
    description: "Deploy basic monitoring stack (Prometheus, Grafana, Redis)"
  },
  domain: {
    topic: "domain_delegation",
    type: "delegated_domain",
    name: "Domain Delegation",
    image: "./assets/web.png",
    url: "/solutions/domain_delegation",
    description: "Delegate your domains to our gateways"
  },
  fourtosixgw: {
    topic: "4to6gw",
    type: "4to6gw",
    name: "4 to 6 Gateway",
    image: "./assets/4to6.png",
    url: "/solutions/4to6gw",
    description: "4to6 Gateway gives you access to IPv6 networks using a wireguard tunnel"
  },
}


const APPS = {
  wiki: {
    topic: "wiki_deploy",
    type: "wiki",
    name: "Wiki",
    image: "./assets/doc-flat.svg",
    url: "/solutions/deploy_wiki",
    description: "Publish a wiki like https://wiki.threefold.io/"
  },
  website: {
    topic: "website_deploy",
    type: "website",
    name: "Website",
    image: "./assets/web.png",
    url: "/solutions/deploy_website",
    description: "Publish a website like https://www.threefold.io/"
  },
  blog: {
    topic: "blog_deploy",
    type: "blog",
    name: "Blog",
    image: "./assets/blog.png",
    url: "/solutions/deploy_blog",
    description: "Publish a blog like https://blog.threefold.io/"
  },
  mattermost: {
    topic: "mattermost",
    type: "mattermost",
    name: "Mattermost",
    image: "./assets/mattermost.png",
    url: "/solutions/mattermost",
    description: "Mattermost is a flexible, open source messaging platform that enables secure team collaboration"
  },
  peertube: {
    topic: "peertube",
    type: "peertube",
    name: "Peertube",
    image: "./assets/peertube.png",
    url: "/solutions/peertube",
    description: "Peertube is a free and open-source, decentralized video platform that uses P2P technology to reduce load on individual servers."
  },
  discourse: {
    topic: "discourse",
    type: "discourse",
    name: "Discourse",
    image: "./assets/discourse.png",
    url: "/solutions/discourse",
    description: "Discourse is an open source Internet forum and mailing list management software application."
  },
  cryptpad: {
    topic: "cryptpad_deploy",
    type: "cryptpad",
    name: "Cryptpad",
    image: "./assets/cryptpad.png",
    url: "/solutions/cryptpad_deploy",
    description: "CryptPad is the Zero Knowledge realtime collaborative editor."
  },
  taiga: {
    topic: "taiga_deploy",
    type: "taiga",
    name: "Taiga",
    image: "./assets/taiga.png",
    url: "/solutions/taiga_deploy",
    description: "Build your 'All in one' Taiga solution"
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
