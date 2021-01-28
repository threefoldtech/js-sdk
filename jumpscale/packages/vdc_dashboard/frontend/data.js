const DECENTRALIZED_OFFICE = {
    titleToolTip: null,
    apps: {
        taiga: {
            name: "Taiga",
            type: "taiga",
            image: "./assets/taiga.png",
            disable: false,
            helpLink: "https://now.threefold.io/docs/dmcircles/",
            description: "Taiga is a P2P alternative to centralized project management tool for multi-functional agile teams."
        },
        cryptpad: {
            name: "Cryptpad",
            type: "cryptpad",
            image: "./assets/cryptpad.png",
            disable: false,
            helpLink: "https://now.threefold.io/docs/dmcollab/",
            description: "Cryptpad is a fully-secured, encrypted alternative to popular office tools and cloud services."
        },
        mattermost: {
            name: "Mattermost",
            type: "mattermost",
            image: "./assets/mattermost.png",
            disable: false,
            helpLink: "https://now.threefold.io/now/docs/mattermost/",
            description: "Mattermost is a flexible, open source messaging platform that enables secure team collaboration."
        },
        crm: {
            name: "CRM",
            type: "crm",
            image: "./assets/crm.png",
            disable: true,
            helpLink: "https://now.threefold.io/now/docs/dmcustomers/",
            description: "Full featured Customer Relationship Management system."
        },
        zeroci: {
            name: "ZeroCI",
            type: "zeroci",
            image: "./assets/zero-ci-dark.png",
            disable: false,
            helpLink: "https://now.threefold.io/now/docs/zeroci/",
            description: "Continuous integration system useful for all programming languages."
        },
        commento: {
            name: "Commento",
            type: "commento",
            image: "./assets/commento.png",
            disable: true,
            helpLink: "https://now.threefold.io/now/docs/commento/",
            description: "Collaborate on online content without giving up your privacy."
        },

    },
}


const DECENTRALIZED_WE = {
    titleToolTip: null,
    apps: {
        blog: {
            name: "Blog",
            type: "blog",
            image: "./assets/blog.png",
            disable: false,
            helpLink: "https://now.threefold.io/now/docs/publishing-tool/",
            description: "Blog is a P2P alternative to centralized blogging platforms like Tumblr or Blogspot."
        },
        website: {
            name: "Website",
            type: "website",
            image: "./assets/web.png",
            disable: false,
            helpLink: "https://now.threefold.io/now/docs/publishing-tool/",
            description: "Website is a P2P alternative to centralized cloud-hosted websites. Host your own website with access via a public web address."
        },

        wiki: {
            name: "Wiki",
            type: "wiki",
            image: "./assets/doc-flat.svg",
            disable: false,
            helpLink: "https://now.threefold.io/now/docs/publishing-tool/",
            description: "Wiki is a versatile online encyclopedia builder, accessible via a public web address."
        },
        discourse: {
            name: "Discourse",
            type: "discourse",
            image: "./assets/discourse.png",
            disable: false,
            helpLink: "https://now.threefold.io/now/docs/discourse/",
            description: "Discourse is an open source Internet forum and mailing list management software application built to educate members about civil community engagement."
        },
        kubeapps: {
            name: "Kubeapps",
            type: "kubeapps",
            image: "./assets/kubeapps.png",
            disable: false,
            helpLink: "https://now.threefold.io/now/docs/kubeapps/",
            description: "Kubeapps is a web-based UI for deploying and managing applications in Kubernetes clusters."
        },
        peertube: {
            name: "Peertube",
            type: "peertube",
            image: "./assets/peertube.png",
            disable: false,
            helpLink: "https://now.threefold.io/now/docs/video-sharing/",
            description: "Peertube is an open-source video platform that uses peer-to-peer technologies to reduce load on individual servers when viewing videos."
        },
        meetings: {
            name: "Video Chat",
            type: "meetings",
            image: "./assets/video_chat.png",
            disable: false,
            helpLink: "https://now.threefold.io/now/docs/video-conf/",
            description: "P2P alternative to centralised video conferencing solution such as Zoom."
        },
        documentserver: {
            name: "Document Server",
            type: "documentserver",
            image: "./assets/document_server.jpg",
            disable: false,
            helpLink: "https://now.threefold.io/now/docs/documentserver/",
            description: "Document Server is a free collaborative online office suite comprising viewers and editors for texts, spreadsheets and presentations, fully compatible with Office Open XML formats: .docx, .xlsx, .pptx and enabling collaborative editing in real time"
        },
        filebrowser: {
            name: "File Browser",
            type: "filebrowser",
            image: "./assets/file_browser.jpg",
            disable: false,
            helpLink: "https://now.threefold.io/now/docs/filebrowser/",
            description: "File browser is an open source solution that provides a file managing interface"
        },
        virtualspaces: {
            name: "Virtual Spaces",
            type: "virtualspaces",
            image: "./assets/virtual_spaces.png",
            disable: true,
            helpLink: "https://now.threefold.io/now/docs/virtual-spaces/",
            description: "Meetup experiences and collaboration in virtual reality."
        },
        knowledgebase: {
            name: "Knowledge Base",
            type: "knowledgebase",
            image: "./assets/_base.png",
            disable: true,
            helpLink: "https://now.threefold.io/now/docs/knowledge-base/",
            description: "A simple, self-hosted, easy-to-use platform for organizing and storing information."
        },
    },
}

const DECENTRALIZED_DEV = {
    titleToolTip: null,
    apps: {
        gitea: {
            name: "Gitea",
            type: "gitea",
            image: "./assets/gitea.png",
            disable: false,
            helpLink: "https://now.threefold.io/now/docs/gitea/",
            description: "Gitea is a painless self-hosted Git service. It is similar to GitHub, Bitbucket, and GitLab."
        },
        serverless: {
            name: "Serverless",
            type: "serverless",
            image: "./assets/serverless.png",
            disable: true,
            helpLink: "https://now.threefold.io/now/docs/serverless/",
            description: "Collaborate on online content without giving up your privacy."
        },
        gridsome: {
            name: "Gridsome",
            type: "gridsome",
            image: "./assets/gridsome.png",
            disable: true,
            helpLink: "https://now.threefold.io/now/docs/gridsome/",
            description: "Gridsome makes it easy to build Jamstack websites using data from multiple sources."
        },
        monitoringstack: {
            name: "Monitoring Stack",
            type: "monitoringstack",
            image: "./assets/monitoring.png",
            disable: false,
            helpLink: "",
            description: "Monitoring Stack makes it easy to monitor your VDC using Grafana, Prometheus, Redis"
        },
        etcd: {
            name: "ETCD",
            type: "etcd",
            image: "./assets/etcd.png",
            disable: false,
            helpLink: "",
            description: "A distributed, reliable key-value store for the most critical data of a distributed system. Used by kubectl"
        },
    },
}

const BC_SOLUTIONS = {
    titleToolTip: null,
    apps: {
        dash: {
            name: "Dash",
            type: "dash",
            image: "./assets/dash.png",
            disable: true,
            helpLink: "https://now.threefold.io/now/docs/dash/",
            description: "Open source peer-to-peer cryptocurrency with a strong focus on the payments industry."
        },
        digibyte: {
            name: "Digibyte",
            type: "digibyte",
            image: "./assets/digibyte.png",
            disable: false,
            helpLink: "https://now.threefold.io/now/docs/digibyte/",
            description: "Safest, fastest, longest, and most decentralized UTXO blockchains in existence."
        },
        elrond: {
            name: "Elrond",
            type: "elrond",
            image: "./assets/elrond.png",
            disable: true,
            helpLink: "https://now.threefold.io/now/docs/elrond/",
            description: "The internet-scale blockchain, designed from scratch to bring a 1000-fold cumulative improvement in throughput and execution speed."
        },
        harmony: {
            name: "Harmony",
            type: "harmony",
            image: "./assets/harmony.png",
            disable: true,
            helpLink: "https://now.threefold.io/now/docs/harmony/",
            description: "Fast and open blockchain for decentralized applications."
        },
        Matic: {
            name: "Matic",
            type: "Matic",
            image: "./assets/matic.png",
            disable: true,
            helpLink: "https://now.threefold.io/now/docs/matic/",
            description: "Decentralized scalability platform solution using an adapted version of the Plasma framework that empowers Ethereum-based DApps."
        },
        neo: {
            name: "Neo",
            type: "neo",
            image: "./assets/neo.png",
            disable: true,
            helpLink: "https://now.threefold.io/now/docs/neo/",
            description: "Scalable, fast, and ultra-secure Blockchain drove by a global community of developers and node operators."
        },
        scale: {
            name: "Scale",
            type: "scale",
            image: "./assets/Skale.png",
            disable: true,
            helpLink: "https://now.threefold.io/now/docs/skalelabs/",
            description: "An elastic blockchain network that gives developers the ability to easily provision highly configurable chains compatible with Ethereum."
        },
        tomochain: {
            name: "TomoChain",
            type: "tomochain",
            image: "./assets/TomoChain.png",
            disable: true,
            helpLink: "https://now.threefold.io/now/docs/tomochain/",
            description: "Scalable blockchain-powered via Proof-of-Stake Voting consensus and used commercially by companies globally."
        },
        waykichain: {
            name: "WaykiChain",
            type: "waykichain",
            image: "./assets/WaykiChain.png",
            disable: true,
            helpLink: "https://now.threefold.io/now/docs/waykichain/",
            description: "Prominent blockchain platform based in China with a global community."
        },
    },
}


const SECTIONS = {
    "All Solutions": {
        titleToolTip: null,
        apps: {
            ...DECENTRALIZED_OFFICE.apps,
            ...DECENTRALIZED_WE.apps,
            ...DECENTRALIZED_DEV.apps,
            ...BC_SOLUTIONS.apps,
        },
    },
    "Decentralized Office": DECENTRALIZED_OFFICE,
    "Decentralized WE": DECENTRALIZED_WE,
    "Decentralized Developer": DECENTRALIZED_DEV,
    "Blockchain Solutions": BC_SOLUTIONS,
}
const KUBERNETES_VM_SIZE_MAP =
{
    1: { "vcpu": 1, "memory": 2, "storage": 50 },
    2: { "vcpu": 2, "memory": 4, "storage": 100 },
    3: { "vcpu": 2, "memory": 8, "storage": 25 },
    4: { "vcpu": 2, "memory": 8, "storage": 50 },
    5: { "vcpu": 2, "memory": 8, "storage": 200 },
    6: { "vcpu": 4, "memory": 16, "storage": 50 },
    7: { "vcpu": 4, "memory": 16, "storage": 100 },
    8: { "vcpu": 4, "memory": 16, "storage": 400 },
    9: { "vcpu": 8, "memory": 32, "storage": 100 },
    10: { "vcpu": 8, "memory": 32, "storage": 200 },
    11: { "vcpu": 8, "memory": 32, "storage": 800 },
    12: { "vcpu": 16, "memory": 64, "storage": 200 },
    13: { "vcpu": 16, "memory": 64, "storage": 400 },
    14: { "vcpu": 16, "memory": 64, "storage": 800 },
    15: { "vcpu": 1, "memory": 2, "storage": 25 },
    16: { "vcpu": 2, "memory": 4, "storage": 50 },
    17: { "vcpu": 4, "memory": 8, "storage": 50 },
    18: { "vcpu": 1, "memory": 1, "storage": 25 },
}
