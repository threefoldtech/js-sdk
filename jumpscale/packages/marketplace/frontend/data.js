const SOLUTIONS = {
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
    description: "Deploy a Kubernetes cluster with zdb using a chatflow. In this guide we will walk you through the provisioning of a full-blown kubernetes cluster on the TF grid. We will then see how to connect to it and interact using kubectl on our local machine. Finally we will go through some examples use cases to grasp the features offered by the cluster."
  },
  minio: {
    name: "Minio",
    type: "minio",
    image: "./assets/minio.png",
    description: "MinIO is a high performance object storage. With the assist of the chatflow the user will deploy a machine with MinIO along with the number of zdbs needed for storage."
  },
  gitea: {
    name: "Gitea",
    type: "gitea",
    image: "./assets/gitea.png",
    description: "Gitea is a painless self-hosted Git service. It is similar to GitHub, Bitbucket, and GitLab."
  },
  pools: {
    name: "Pools",
    type: "pools",
    image: "./assets/pool.png",
    description: "Reserve capacity on the grid to deploy the solutions on.",
  },
  network: {
    name: "Network",
    type: "network",
    image: "./assets/network.png",
    description: "Deploy a network on the grid to connect your solutions together."
  },
  threebot: {
    name: "3Bot",
    type: "threebot",
    image: "./assets/3bot.png",
    description: "Deploy your 3Bot on container."
  },
  expose: {
    name: "Solution Expose",
    type: "exposed",
    image: "./assets/expose.png",
    description: "Access your web application running on the grid using a FQDN"
  },
  flist: {
    name: "Generic Container",
    type: "flist",
    image: "./assets/flist.png",
    description: "Spawn a container using specific flist provided by the user in the chatflow."
  },
  monitoring: {
    name: "Monitoring",
    type: "monitoring",
    image: "./assets/monitoring.png",
    description: "Deploy basic monitoring stack (Prometheus, Grafana, Redis)"
  },
  domain: {
    name: "Domain Delegation",
    type: "delegated_domain",
    image: "./assets/web.png",
    description: "Delegate your domains to our gateways"
  },
  fourtosixgw: {
    name: "4 to 6 Gateway",
    type: "4to6gw",
    image: "./assets/4to6.png",
    description: "4to6 Gateway gives you access to IPv6 networks using a wireguard tunnel"
  },
}


const APPS = {
  wiki: {
    name: "Wiki",
    type: "wiki",
    image: "./assets/doc-flat.svg",
    description: "Publish a wiki like https://wiki.threefold.io/"
  },
  website: {
    name: "Website",
    type: "website",
    image: "./assets/web.png",
    description: "Publish a website like https://www.threefold.io/"
  },
  blog: {
    name: "Blog",
    type: "blog",
    image: "./assets/blog.png",
    description: "Publish a blog like https://blog.threefold.io/"
  },
  mattermost: {
    name: "Mattermost",
    type: "mattermost",
    image: "./assets/mattermost.png",
    description: "Mattermost is a flexible, open source messaging platform that enables secure team collaboration"
  },
  peertube: {
    name: "Peertube",
    type: "peertube",
    image: "./assets/peertube.png",
    description: "Peertube is a free and open-source, decentralized video platform that uses P2P technology to reduce load on individual servers."
  },
  discourse: {
    name: "Discourse",
    type: "discourse",
    image: "./assets/discourse.png",
    description: "Discourse is an open source Internet forum and mailing list management software application."
  },
  cryptpad: {
    name: "Cryptpad",
    type: "cryptpad",
    image: "./assets/cryptpad.png",
    description: "CryptPad is the Zero Knowledge realtime collaborative editor."
  },
  taiga: {
    name: "Taiga",
    type: "taiga",
    image: "./assets/taiga.png",
    description: "Taiga is the project management tool for multi-functional agile teams. Build your 'All in one' Taiga solution"
  },
}
