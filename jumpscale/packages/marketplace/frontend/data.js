const COLLAB_TOOLS = {
    titleToolTip: null,
    apps: {
        taiga: {
            name: "Taiga",
            type: "taiga",
            image: "./assets/taiga.png",
            disable: false,
            helpLink: "https://now10.threefold.io/docs/dmcircles/",
            description: "Taiga is a P2P alternative to centralized project management tool for multi-functional agile teams."
        },
        cryptpad: {
            name: "Cryptpad",
            type: "cryptpad",
            image: "./assets/cryptpad.png",
            disable: false,
            helpLink: "https://now10.threefold.io/docs/dmcollab/",
            description: "Cryptpad is a fully-secured, encrypted alternative to popular office tools and cloud services."
        },
        mattermost: {
            name: "Mattermost",
            type: "mattermost",
            image: "./assets/mattermost.png",
            disable: false,
            helpLink: "https://now10.threefold.io/docs",
            description: "Mattermost is a flexible, open source messaging platform that enables secure team collaboration."
        },
    },
}


const WEB_SOCIAL = {
    titleToolTip: null,
    apps: {
        blog: {
            name: "Blog",
            type: "blog",
            image: "./assets/blog.png",
            disable: false,
            helpLink: "https://now10.threefold.io/docs/blog-publisher/",
            description: "Blog is a P2P alternative to centralized blogging platforms like Tumblr or Blogspot."
        },
        website: {
            name: "Website",
            type: "website",
            image: "./assets/web.png",
            disable: false,
            helpLink: "https://now10.threefold.io/docs/website-publisher/",
            description: "Website is a P2P alternative to centralized cloud-hosted websites. Host your own website with access via a public web address."
        },

        wiki: {
            name: "Wiki",
            type: "wiki",
            image: "./assets/doc-flat.svg",
            disable: false,
            helpLink: "https://now10.threefold.io/docs/wiki-publisher/",
            description: "Wiki is a versatile online encyclopedia builder, accessible via a public web address."
        },
        discourse: {
            name: "Discourse",
            type: "discourse",
            image: "./assets/discourse.png",
            disable: false,
            helpLink: "https://now10.threefold.io/docs",
            description: "Discourse is an open source Internet forum and mailing list management software application built to educate members about civil community engagement."
        },
        peertube: {
            name: "Peertube",
            type: "peertube",
            image: "./assets/peertube.png",
            disable: false,
            helpLink: "https://now10.threefold.io/docs/video-sharing/",
            description: "Peertube is an open-source video platform that uses peer-to-peer technologies to reduce load on individual servers when viewing videos."
        },
        meetings: {
            name: "Meetings",
            type: "meetings",
            image: "./assets/meetings.png",
            disable: false,
            helpLink: "https://now10.threefold.io/video-conf",
            description: "A decentralized meeting app that enables you to have video calls and chat with colleagues or friends."
        }
    },
}

const DEV_TOOLS = {
    titleToolTip: null,
    apps: {
        gitea: {
            name: "Gitea",
            type: "gitea",
            image: "./assets/gitea.png",
            disable: false,
            helpLink: "https://now10.threefold.io/docs/gitea/#what-is-gitea-",
            description: "Gitea is a painless self-hosted Git service. It is similar to GitHub, Bitbucket, and GitLab."
        },
    },
}

const SECTIONS = {
    "All Solutions": {
        titleToolTip: null,
        apps: {
            ...COLLAB_TOOLS.apps,
            ...WEB_SOCIAL.apps,
            ...DEV_TOOLS.apps,
        },
    },
    "Collaboration Tools": COLLAB_TOOLS,
    "Web & Social": WEB_SOCIAL,
    "Developer Tools": DEV_TOOLS,
}
