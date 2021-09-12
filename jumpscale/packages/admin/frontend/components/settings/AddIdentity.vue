<template>
  <base-dialog title="Add identity" v-model="dialog" :error="error" :info="info" :loading="loading" :persistent="true">
    <template #default>
      <v-form>
        <v-text-field v-model="form.display_name" label="Display name" @blur="checkInstanceName(form.display_name)" dense>
        <v-tooltip slot="append" left>
            <template v-slot:activator="{ on, attrs }">
              <v-btn icon v-bind="attrs" v-on="on" :tabindex="10">
                <v-icon color="grey lighten-1"> mdi-help-circle </v-icon>
              </v-btn>
            </template>
            <span>The display name is used to reference the registered identity on TFGrid across the 3Bot.</span>
        </v-tooltip>
        </v-text-field>
        <v-text-field v-model="form.tname" label="3Bot name" @blur="checkTNameExists(form.tname)" dense></v-text-field>
        <v-text-field v-model="form.email" label="Email" dense></v-text-field>
        <!-- Start Admins -->
        <v-combobox
          v-model="selectedAdmins"
          :items="[]"
          chips
          clearable
          label="Add admins"
          multiple
          solo
        >
          <template v-slot:selection="{ attrs, item, select, selected }">
            <v-chip
              v-bind="attrs"
              :input-value="selected"
              close
              @click="select"
              @click:close="removeFromAdmins(item)"
              color="primary"
            >
              <span>{{ item }}</span>
            </v-chip>
          </template>
        </v-combobox>
        <!-- End Admins -->
        <v-text-field v-model="words" label="Words" dense>
          <template v-slot:append>
              <v-btn
                v-if="allowCreatMnemonics"
                color="info"
                class="mx-2 mb-2"
                :tabindex="10"
                @click="getMnemonics()">
                create Words
              </v-btn>
          </template>
        </v-text-field>
        <v-select v-model="selected_explorer" label="Explorer type" @change="checkTNameExists(form.tname)" :items="Object.keys(explorers)" dense></v-select>
      </v-form>
    </template>
    <template #actions>
      <v-btn text color="red" @click="closeDialog()">Close</v-btn>
      <v-btn text color="green" :disabled="disable" @click="submit">Add</v-btn>
    </template>
  </base-dialog>
</template>

<script>

module.exports = {
  mixins: [dialog],
  data () {
    return {
      explorers: {
        "Main Network": {url: "https://explorer.grid.tf", type: "main"},
        "Test Network": {url: "https://explorer.testnet.grid.tf", type: "testnet"},
        "Dev Network": {url: "https://explorer.devnet.grid.tf", type: "devnet"},

      },
      selected_explorer: "Main Network",
      display_name:"",
      words: "",
      allowCreatMnemonics: false,
      selectedAdmins: [],
    }
  },
  computed: {
    disable() {
      if(!this.form.display_name || !this.form.tname || !this.form.email || !this.words || !this.selected_explorer || this.error !== ""){
        return true;
      }
      return false;
    },
  },
  methods: {
    submit () {
        this.loading = true
        this.error = null
        this.$api.admins.getCurrentUser()
          .then(({ data }) => {
            if (data.username) {
              if (this.selectedAdmins.indexOf(data.username) === -1) {
                this.selectedAdmins.push(data.username);
              }
              
              return this.$api
                         .identities
                         .add(
                           this.form.display_name, 
                           this.form.tname, 
                           this.form.email, 
                           this.words, 
                           this.explorers[this.selected_explorer].type, 
                           this.selectedAdmins);
            }
            this.error = "Couldn't load current username.";
            return null;
          })
          .then((res) => {
            if (res) {
              this.done("New Identity added", "success")
            }
          })
          .catch(error => {
            this.error = error.response.data.error
          })
          .finally(() => {
              this.loading = false
          })
    },
    getMnemonics(){
      this.$api.identities.generateMnemonic().then((response) => {
        mnemonics = JSON.parse(response.data).data
        this.allowCreatMnemonics = false;
        this.words = mnemonics;
      })
    },
    checkTNameExists(tname){
      if(tname){
        this.$api.identities.checkTNameExists(tname, this.explorers[this.selected_explorer].type).then((response) => {
          res = JSON.parse(response.data).data
          if(res){
              this.allowCreatMnemonics = false;
              this.words = "";
              this.info = "This 3Bot name existed in the explorer, you have to enter the right words";
          }
          else{
            this.info = "";
            this.allowCreatMnemonics = true;
          }
        })
      }
      else {
        this.allowCreatMnemonics = false;
      }
    },
    checkInstanceName(instance_name){
      if(instance_name){
        this.$api.identities.checkInstanceName(instance_name).then((response) => {
          res = JSON.parse(response.data).data
          if(res){
            this.error = "This instance name is existed, Enter anther one.";
          }
          else{
            this.error = "";
          }
        })
      }
    },
    closeDialog(){
      this.close()
      // clear dialog
      this.display_name = this.tname = this.email = this.words = "";
    },
    removeFromAdmins(admin) {
      this.selectedAdmins = this.selectedAdmins.filter(a => a !== admin);
    },
  }
}
</script>
