<template>
  <v-card flat height="100%" class="pa-5" outlined>
    <v-card-text>
      <p class="display-1 text--primary">Threefold Marketplace</p>
      <div class="text--primary">
        <h1
          id="the-threefold-grid-a-high-level-introduction"
        >The ThreeFold Grid: A High Level Introduction</h1>
        <p>
          <img
            width="95%"
            src="https://github.com/threefoldfoundation/info_foundation/raw/master/src/grid/img/tf_principle_banner.png"
            alt="TF Banner"
          />
        </p>
        <p>
          Originally the internet was intended to be fully peer2peer, today thats not the case. Few datacenters in centralized locations deliver all the capacity for the current internet. This capacity is mainly storage &amp; compute capacity.
          ThreeFold wants to restore this situation.
        </p>
        <p>Today the ThreeFold Grid (TFGrid) is the largest peer-to-peer grid of Internet (compute, storage and network) capacity in the world. The sum of all IT capacity in the TFGrid today is larger than the sum of all IT capacity as used for all blockchain projects. This may sound a lot but actually its still small compared to the massive centralized cloud vendors.</p>
        <p>The ThreeFold Project needs thousands of new farmers who want to extend the ThreeFold Grid to create an upgraded internet where all data is private and all people can be free again.</p>
        <p>The ThreeFold Grid is a platform on which any internet experience (or service) can be built on.</p>
        <ul>
          <li>Any application which can run on linux (which is +- all) can run on top of the TFGrid.</li>
          <li>There are already more than 20 projects who are committed to run their workloads on top of the TFGrid.</li>
        </ul>
        <p>The ThreeFold Grid needs computers (servers) to function. Servers of all shapes and sizes can be added to the ThreeFold Grid, by anyone, anywhere in the world. Zero-OS is an opensource operating system which needs to be run on the servers to make them extend the grid. People that add this hardware to the grid are called farmers. This is a fully decentralized process, any farmer downloads the Zero-OS operating system and boots his/her servers (which we call 3nodes). The 3nodes will register themselves in a directory called TFDirectory and users can then find the capacity they need to run their applications.</p>
        <p>A dedicated digital currency called TFT has been created to allow anyone to sell/buy this IT capacity (Storage,Compute, Network).</p>
        <h4 id="the-grid-is-active">The grid is active</h4>
        <ul>
          <li>+18000 CPU cores</li>
          <li>+90,000,000 GB of online storage</li>
        </ul>
        <p>The system is still not distributed enough though, there are only 50-60 locations now. The Foundation wants to organize promotion activities to find more farmers but needs more funding (see TDE = Token Distribution Event).</p>
        <h4 id="how-mature-is-the-tfgrid-">How mature is the TFGrid?</h4>
        <ul>
          <li>Our Zero-OS is beta quality and is at 2nd major release.</li>
          <li>The workloads can be registered using json format for our smart contract for IT layer.</li>
          <li>Experts can use any development language to use the grid as is by using this smart contract for IT layer.</li>
          <li>We can use some help to improve the documentation though.</li>
          <li>The marketplace you find here makes your life more easy to play with the ZOS 2.2 (0.4) on TFGrid 2.2</li>
        </ul>
        <h4
          id="there-is-also-an-automation-layer-called-3bot"
        >There is also an automation layer called 3bot</h4>
        <ul>
          <li>3bot is your virtual system administrator and here you can see our brand new 2.2 version, deploy your own version on the marketplace (v2.2).</li>
          <li>Its a very powerful tool to allow you to automate &amp; manage thousands of virtual workload.</li>
          <li>Python language can be used to extend this tool and make it your own.</li>
          <li>This new admin panel is alpha quality, be reminded that the workload itself is running on Zero-OS and the smart contract for IT layer which is beta quality.</li>
        </ul>
        <h4 id="terms-and-conditions">Terms and Conditions</h4>
        <p>
          you cannot use this marketplace or the 3bot unless you agree with
          see
          <a
            target="_blank"
            href="https://wiki.threefold.io/#/terms_conditions"
          >Terms and Conditions</a>
        </p>
      </div>
    </v-card-text>
  </v-card>
</template>

<script>
module.exports = {
  mounted() {
    this.$root.$emit("sidebar", true);
  },
};
</script>
