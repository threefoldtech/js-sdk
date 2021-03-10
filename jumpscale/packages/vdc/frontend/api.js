// const axios = require('axios')

const apiClient = {
  content: {
    get: (url) => {
      return axios({
        url: url
      })
    }
  },
  admins: {
    getCurrentUser: () => {
      return axios({
        url: "/auth/authenticated/"
      })
    },
  },
  explorers: {
    get: () => {
      return axios({
        url: "/actors/admin/get_explorer/"
      })
    },
  },
  solutions: {
    listVdcs: () => {
      return axios({
        url: `/vdc/api/vdcs`,
        method: "get",
        headers: { 'Content-Type': 'application/json' }
      })

    },
    getVdcInfo: (name) => {
      return axios({
        url: `/vdc/api/vdcs/` + name,
        headers: { 'Content-Type': 'application/json' },
        method: "get"
      })
    },
    deleteVDC: (name) => {
      return axios({
        url: `/vdc/api/vdcs/delete`,
        method: "post",
        data: { name: name },
        headers: { 'Content-Type': 'application/json' }
      })
    },
  },
  license: {
    accept: () => {
      return axios({
        url: `/vdc/api/accept/`,
        method: "get"
      })
    },
  },
  wallets: {
    walletQRCodeImage: (address, amount, scale) => {
      return axios({
        url: `/vdc/api/wallet/qrcode/get`,
        method: "post",
        data: { address: address,amount: amount, scale: scale},
        headers: { 'Content-Type': 'application/json' }
      })
    },
  },

}
