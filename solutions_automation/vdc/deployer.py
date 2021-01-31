from solutions_automation.vdc.dashboard.vdc import VDCAutomated


def deploy_vdc(solution_name, vdc_secert, vdc_plan):
    return VDCAutomated(solution_name=solution_name, vdc_secert=vdc_secert, vdc_plan=vdc_plan)
