class VDCBaseComponent:
    def __init__(self, vdc_deployer):
        self.vdc_deployer = vdc_deployer
        self.vdc_instance = self.vdc_deployer.vdc_instance
        self.bot = self.vdc_deployer.bot
        self.vdc_name = self.vdc_deployer.vdc_name
        self.identity = self.vdc_deployer.identity
        self.vdc_uuid = self.vdc_deployer.vdc_uuid

    @property
    def wallet(self):
        return self.vdc_deployer.wallet

    @property
    def explorer(self):
        return self.vdc_deployer.explorer

    @property
    def zos(self):
        return self.vdc_deployer.zos
