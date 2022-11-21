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
