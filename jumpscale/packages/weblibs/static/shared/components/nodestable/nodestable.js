module.exports = new Promise(async (resolve, reject) => {
  const vuex = await import("/weblibs/vuex/vuex.esm.browser.js");
  const { moment } = await import("/weblibs/moment/moment.min.js");
  const { momentDurationFormat } = await import(
    "/weblibs/moment/moment-duration-format.js"
  );
  momentDurationFormat(moment);
  resolve({
    name: "nodestable",
    props: ['farmselected'],
    components: {
      nodeinfo: httpVueLoader("/weblibs/shared/components/nodeinfo/index.vue")
    },
    data() {
      return {
        showDialog: false,
        dilogTitle: "title",
        dialogBody: "",
        dialogActions: [],
        dialogImage: null,
        block: null,
        showBadge: true,
        menu: false,
        loadedNodes: false,
        itemsPerPage: 4,
        expanded: [],
        searchNodes: "",
        headers: [
          { text: "ID", value: "id" },
          { text: "Uptime", value: "uptime" },
          { text: "Version", value: "version" },
          { text: "Farmer", value: "farmer" },
          { text: "Status", value: "status", align: "center" }
        ]
      };
    },
    computed: {
      ...vuex.mapGetters([
        "registeredNodes",
        "registeredFarms",
        "nodes"
      ]),
      // Parse nodelist to table format here
      parsedNodesList: function() {
        const nodeList = this.nodes ? this.nodes : this.registeredNodes
        const parsedNodes = nodeList.filter(node => !this.farmselected || (this.farmselected.id === node.farm_id)).map(node => {
          const uptime = moment.duration(node.uptime, "seconds").format();

          const farmer = _.find(this.registeredFarms, farmer => {
            return farmer.id === node.farm_id;
          });

          // initialize farmer name with farmer_id from node in case farmer is not found
          let farmerName = node.farm_id;
          if (farmer) {
            farmerName = farmer.name;
          }

          return {
            uptime,
            version: node.os_version,
            id: node.node_id,
            farmer: farmerName,
            name: "node " + node.node_id,
            totalResources: node.total_resources,
            reservedResources: node.reserved_resources,
            usedResources: node.used_resources,
            updated: new Date(node.updated * 1000),
            status: this.getStatus(node),
            location: node.location
          };
        });
        return parsedNodes;
      }
    },
    mounted () {
      this.resetNodes()
      this.getRegisteredNodes()
    },
    methods: {
      ...vuex.mapActions([
        "getRegisteredNodes",
        "resetNodes"
      ]),
      getStatus(node) {
        const { updated } = node;
        const startTime = moment();
        const end = moment.unix(updated);
        const minutes = startTime.diff(end, "minutes");

        // if updated difference in minutes with now is less then 10 minutes, node is up
        if (minutes < 15) return { color: "green", status: "up" };
        else if (16 < minutes && minutes < 20)
          return { color: "orange", status: "likely down" };
        else return { color: "red", status: "down" };
      },
      truncateString(str) {
        str = str.toString();
        if (str.length < 10) return str;
        return str.substr(0, 10) + "...";
      },
      openNodeDetails(node) {
        const index = this.expanded.indexOf(node);
        if (index > -1) this.expanded.splice(index, 1);
        else this.expanded.push(node);
      },
    }
  });
});
