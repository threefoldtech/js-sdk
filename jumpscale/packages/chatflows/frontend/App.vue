<template>
  <v-app>
    <v-app-bar v-if="$route.query.noheader !== 'yes'" app>
      <img src="/chatflows/static/assets/images/3bot.png" width="24"/>
      <v-spacer></v-spacer>
      <v-menu v-model="menu" :close-on-content-click="false" :nudge-width="200" offset-x>
        <template v-slot:activator="{ on }">
          <v-btn text v-on="on">
            <v-icon left>mdi-account</v-icon> {{userInfo.username}}
          </v-btn>
        </template>
        <v-card>
          <v-list>
            <v-list-item>
              <v-list-item-avatar>
                <v-avatar color="primary">
                  <v-icon dark>mdi-account-circle</v-icon>
                </v-avatar>
              </v-list-item-avatar>
              <v-list-item-content>
                <v-list-item-title>{{userInfo.username}}</v-list-item-title>
                <v-list-item-subtitle>{{userInfo.email}}</v-list-item-subtitle>
              </v-list-item-content>
            </v-list-item>
          </v-list>
          <v-divider></v-divider>
          <v-card-actions>
            <v-btn block text>
              <v-icon color="gray" class="mr-2" left>mdi-logout-variant</v-icon> Logout
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-menu>

    </v-app-bar>
    <v-content>
      <div class="chat-container text-center">
          <h1 class="display-2 font-weight-light">Zero Chat Bot</h1><br><br>

          <v-card v-if="end" class="mx-auto px-5 py-10" width="50%" raised shaped>
            <v-card-text>
              <span class="display-1 font-regular primary--text">
                Chat has ended
              </span><br><br>
              <v-btn color="primary" class="px-5" width="250" outlined large @click="restart">
                <v-icon left>mdi-refresh</v-icon> Restart
              </v-btn>
            </v-card-text>
          </v-card>

          <v-card v-if="work && !end" :disabled="loading" :loading="loading" class="mx-auto" width="70%" min-height="350" raised shaped>
            <div class="chat">
              <v-toolbar flat>
                <v-toolbar-title v-if="work.info.title" class="headline font-regular primary--text">
                  {{work.info.title}}
                </v-toolbar-title>
                <v-spacer></v-spacer>
                <v-btn color="primary" @click="restart" icon large>
                  <v-icon>mdi-refresh</v-icon>
                </v-btn>
              </v-toolbar>

              <v-card-text style="text-align:left">
                <v-form ref="form" :lazy-validation="true" @submit.prevent>
                  <component
                    v-model="state[stepId]"
                    :key="stepId"
                    :is="categories[this.work.payload.category]"
                    :payload="this.work.payload"
                  />
                </v-form>

              </v-card-text>

              <div class="text-center mt-10">
                <v-icon style="opacity: 0.8; padding-left:1px" x-small v-for="i in work.info.steps" :key="i" :color="i <= work.info.step ? 'primary' : '#E5E7E9'">mdi-checkbox-blank-circle</v-icon>
              </div>

              <v-card-actions>
                <v-btn color="primary" raised x-large class="px-5" min-width="120" @click="back" :disabled="backButtonDisable">
                  {{work.info.first_slide ? 'Previous step' : 'Back'}}
                </v-btn>
                <v-spacer></v-spacer>
                <v-btn color="primary" raised x-large class="px-5" min-width="120" @click="next" :loading="loading" :disabled="nextButtonDisable">Next</v-btn>
              </v-card-actions>
            </div>
          </v-card>
      </div>
    </v-content>
  </v-app>
</template>

<script>

  const axios = require('axios')
  const baseUrl = "/chatflows/actors/chatbot"

  module.exports =  {
    data () {
      return {
        state: {},
        sessionId: null,
        work: null,
        loading: true,
        end: false,
        menu: false,
        topic: TOPIC,
        noheader: NOHEADER,
        userInfo: {username: USERNAME, email: EMAIL}
      }
    },
    computed: {
      nextButtonDisable () {
        return ['error', 'loading', 'infinite_loading'].includes(this.work.payload.category)
      },
      backButtonDisable () {
        return !this.work.info.previous || ['loading', 'infinite_loading'].includes(this.work.payload.category)
      },
      stepId () {
        return `${this.work.info.step}_${this.work.info.slide}`
      }
    },
    methods: {
      validate() {
        return this.$refs["form"].validate()
      },
      handleResponse (response) {
        let payload = response.payload
        switch (payload.category) {
          case 'end':
            this.end = true
            break
          case 'user_info':
            this.sendUserInfo()
            break
          case 'redirect':
            this.redirect(payload.url)
          default:
            this.handlerWork(response)
        }
        if (this.end === false) this.getWork()
      },
      handlerWork (work) {
        this.work = work
        if (this.state[this.stepId] === undefined) {
          if (['form', 'multi_choice', 'multi_list_choice', 'location_ask'].includes(this.work.payload.category)) {
            this.$set(this.state, this.stepId, Array())
          }
        }
      },
      redirect (url) {
        location.href = url
      },
      sendUserInfo () {
        this.reportWork(JSON.stringify(this.userInfo))
      },
      saveSession () {
        let session = {
          id: this.sessionId,
          state: this.state,
        }
        localStorage.setItem(this.topic, JSON.stringify(session))
      },
      getSession () {
        let session = localStorage.getItem(this.topic)
        if (session) {
          return JSON.parse(session)
        }
      },
      start () {
        let session = this.getSession()
        if (session) {
          this.restoreSession(session)
        } else {
          this.newSession()
        }
      },
      newSession () {
        axios({
          url: `${baseUrl}/new`,
          method: "post",
          data: {
            topic: TOPIC,
            client_ip: CLIENT_IP
          }
        }).then((response) => {
            this.sessionId = response.data.sessionId
            console.log(this.sessionId)
            this.getWork()
        })
      },
      restoreSession (session) {
          this.sessionId = session.id
          this.state = session.state
          this.getWork(true)
      },
      getWork (restore) {
        axios({
          url: `${baseUrl}/fetch`,
          method: "post",
          data: {
            session_id: this.sessionId,
            restore: restore
          }
        }).then((response) => {
            this.loading = false
            this.saveSession()
            this.handleResponse(response.data)
        })
      },
      reportWork (result) {
        axios({
          url: `${baseUrl}/report`,
          method: "post",
          data: {
            session_id: this.sessionId,
            result: result
          }
        })
      },
      next () {
        if (this.validate()) {
          let result = this.state[this.stepId]

          if (typeof result === 'object') {
            result = JSON.stringify(result)
          }

          this.loading = true
          this.reportWork(result)
        }
      },
      back () {
        axios({
          url: `${baseUrl}/back`,
          method: "post",
          data: {
            session_id: this.sessionId
          }
        })
      },
      restart () {
        localStorage.clear()
        location.reload()
      }
    },
    mounted () {
      this.newSession()
      document.body.addEventListener('keypress', (e) => {
        if (e.key == 'Enter') {
          this.next()
        }
      })
    }
  }
</script>
