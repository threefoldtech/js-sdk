<template>
  <v-card flat height="100%" class="pa-5" outlined>
    <v-card-text>
      <p class="display-1 text--primary">The ThreeFold Grid: A High Level Introduction</p>
      <div class="text--primary">
        <p>
          <img width="95%" src="./assets/tf_principle_banner.png" alt="TF Banner" />
        </p>
        <p>
          Originally the internet was intended to be fully peer2peer, today thats not the case. Few datacenters in centralized locations deliver all the capacity for the current internet. This capacity is mainly storage &amp; compute capacity.
          ThreeFold wants to restore this situation.
        </p>
        <p>The ThreeFold Grid is a platform on which any internet experience (or service) can be built on.</p>
        <ul>
          <li>Any application which can run on linux (which is +- all) can run on top of the TFGrid.</li>
          <li>There are already more than 20 projects who are committed to run their workloads on top of the TFGrid.</li>
        </ul>
        <br />
        <p>A dedicated digital currency called TFT has been created to allow anyone to sell/buy this IT capacity (Storage,Compute, Network).</p>
        <h4 id="the-threefold-grid-is-active">The ThreeFold grid is active</h4>
        <p>TFGrid today has:</p>
        <ul>
          <li>+18000 CPU cores</li>
          <li>+90,000,000 GB of online storage</li>
        </ul>
        <br />
        <p>TFGrid is the largest peer-to-peer network of Internet (compute, storage and network) capacity in the world. The sum of all IT capacity in the TFGrid is larger than the sum of all IT capacity as used for all blockchain projects (May 2020). This may sound a lot but actually its still small compared to the massive centralized cloud vendors.</p>
        <p>The system is not distributed enough yet, there are only 50-60 locations, more farmers are needed to grow the grid to its full potential.</p>
        <p>The ThreeFold Grid needs computers (servers) to function. Servers of all shapes and sizes can be added to the ThreeFold Grid, by anyone, anywhere in the world. Zero-OS is an opensource operating system which needs to be run on the servers to make them extend the grid. People who add these computers to the grid are called farmers. This is a fully decentralized process, farmers downloads the Zero-OS operating system and boot their servers (3nodes). The 3nodes will register themselves in a database called TFDirectory and TFGrid users can then find the capacity they need to run their applications.</p>
        <h4 id="how-mature-is-the-tfgrid-">How mature is the TFGrid?</h4>
        <ul>
          <li>Our Zero-OS is beta quality and is at 2nd major release.</li>
          <li>The workloads can be registered using json format for our smart contract for IT layer.</li>
          <li>Experts can use any development language to use the grid as is by using this smart contract for IT layer.</li>
          <li>We can use some help to improve the documentation though.</li>
          <li>The marketplace you find here makes your life more easy to play with the ZOS 2.2 (0.4) on TFGrid 2.2</li>
        </ul>
        <br />
        <h4
          id="there-is-also-an-automation-layer-called-3bot"
        >There is also an automation layer called 3bot</h4>
        <ul>
          <li>3bot is your virtual system administrator and here you can see our brand new 2.2 version, deploy your own version on the marketplace (v2.2).</li>
          <li>Its a very powerful tool to allow you to automate &amp; manage thousands of virtual workload.</li>
          <li>Python language can be used to extend this tool and make it your own.</li>
          <li>This new admin panel is alpha quality, be reminded that the workload itself is running on Zero-OS and the smart contract for IT layer which is beta quality.</li>
        </ul>
        <br />
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
