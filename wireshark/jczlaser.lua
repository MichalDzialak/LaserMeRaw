jcz_proto = Proto("JCZlaser", "JCZ Laser USB protocol, as used by EZCAD2")

opcode = ProtoField.uint16("jczlaser.opcode", "opcode", base.HEX)
param1 = ProtoField.uint16("jczlaser.param1", "param1", base.HEX)
param2 = ProtoField.uint16("jczlaser.param2", "param2", base.HEX)
param3 = ProtoField.uint16("jczlaser.param3", "param3", base.HEX)
param4 = ProtoField.uint16("jczlaser.param4", "param4", base.HEX)
param5 = ProtoField.uint16("jczlaser.param5", "param5", base.HEX)

jcz_proto.fields = { opcode, param1, param2, param3, param4, param5 }

function jcz_proto.dissector(buffer, pinfo, tree)
    length = buffer:len()
    if length == 0 then return end

    pinfo.cols.protocol = jcz_proto.name

    if length == 12 and tostring(pinfo.src) == "host" then
        dissect_immediate(buffer, pinfo, tree)
    elseif length == 3072 and tostring(pinfo.src) == "host" then
        dissect_buffer(buffer, pinfo, tree)
    elseif length == 8 and tostring(pinfo.dst) == "host" then
        dissect_response(buffer, pinfo, tree)
    else
        pinfo.cols.info = "Unknown command type"
        return
    end
end

function dissect_immediate(buffer, pinfo, tree)
    pinfo.cols.info = string.format("JCZ Immediate Command [%s]", immediate_opcodes[buffer(0, 2):le_uint()])
    local subtree = tree:add(jcz_proto, buffer(), "JCZ Immediate Command")
    subtree:add_le(opcode, buffer(0, 2)):append_text(string.format(" [%s]", immediate_opcodes[buffer(0, 2):le_uint()]))
    -- subtree:add_le(opcode, buffer(0, 2)):append_text(string.format(" [%s]", immediate_opcodes[7]))
    subtree:add_le(param1, buffer(2, 2))
    subtree:add_le(param2, buffer(4, 2))
    subtree:add_le(param3, buffer(6, 2))
    subtree:add_le(param4, buffer(8, 2))
    subtree:add_le(param5, buffer(10, 2))
end

function dissect_buffer(buffer, pinfo, tree)
    pinfo.cols.info = "JCZ Buffer Commands"
    local subtree = tree:add(jcz_proto, buffer(), "JCZ buffer Commands")
    for i = 0, 255, 1 do
        opcode_num = buffer(i*12, 2):le_uint()
        command_tree = subtree:add(jcz_proto, buffer(i*12, 12), string.format("Command %d [%s]", i, buffer_opcodes[opcode_num]))
        command_tree:add_le(opcode, buffer(i*12, 2)):append_text(string.format(" [%s]", buffer_opcodes[opcode_num]))
        command_tree:add_le(param1, buffer(i*12+2, 2))
        command_tree:add_le(param2, buffer(i*12+4, 2))
        command_tree:add_le(param3, buffer(i*12+6, 2))
        command_tree:add_le(param4, buffer(i*12+8, 2))
        command_tree:add_le(param5, buffer(i*12+10, 2))
    end
end

function dissect_response(buffer, pinfo, tree)
    pinfo.cols.info = "JCZ Response"
    local subtree = tree:add(jcz_proto, buffer(), "JCZ Response")
    subtree:add_le(param1, buffer(0, 2))
    subtree:add_le(param2, buffer(2, 2))
    subtree:add_le(param3, buffer(4, 2))
    subtree:add_le(param4, buffer(6, 2))
end

local usb_type = DissectorTable.get("usb.bulk")
usb_type:add(0xff, jcz_proto)

immediate_opcodes = {
    [0x0002] = "DisableLaser",
    [0x0003] = "Reset",
    [0x0004] = "EnableLaser",
    [0x0005] = "ExecuteList",
    [0x0007] = "GetVersion",
    [0x0009] = "GetSerialNo",
    [0x0010] = "WriteCorTableLine",
    [0x000a] = "GetListStatus",
    [0x000c] = "GetPositionXY",
    [0x000d] = "GotoXY",
    [0x000e] = "LaserSignalOff",
    [0x000f] = "LaserSignalOn",
    [0x0026] = "SetAxisMotionParam",
    [0x0029] = "MoveAxisTo",
    [0x0028] = "AxisGoOrigin",
    [0x002a] = "GetAxisPos",
    [0x0027] = "SetAxisOriginParam",
    [0x0015] = "WriteCorTable",
    [0x0012] = "ResetList",
    [0x0013] = "RestartList",
    [0x0016] = "SetControlMode",
    [0x0017] = "SetDelayMode",
    [0x0018] = "SetMaxPolyDelay",
    [0x0019] = "SetEndOfList",
    [0x001a] = "SetFirstPulseKiller",
    [0x001c] = "SetTiming",
    [0x001e] = "SetPwmHalfPeriod",
    [0x0006] = "SetPwmPulseWidth",
    [0x001b] = "SetLaserMode",
    [0x001d] = "SetStandby",
    [0x001f] = "StopExecute",
    [0x0020] = "StopList",
    [0x0025] = "ReadPort",
    [0x0021] = "WritePort",
    [0x0022] = "WriteAnalogPort1",
    [0x0023] = "WriteAnalogPort2",
    [0x0024] = "WriteAnalogPortX",
    [0x0062] = "SetFpkParam",
    [0x002e] = "SetFpkParam2",
    [0x0032] = "SetFlyRes",
    [0x0033] = "IPG_OpemMO",
    [0x0034] = "IPG_GETStMO_AP",
    [0x003a] = "ENABLEZ",
    [0x0039] = "ENABLEZ-alt",
    [0x003b] = "SETZDATA",
    [0x003c] = "SetSPISimmerCurrent",
    [0x002b] = "GetFlyWaitCount",
    [0x002d] = "GetMarkCount",
    -- could not find a source for the two codes below, and it's not clear where the dlls call them
    [0x002F] = "FiberConfig1 (?)",
    [0x0030] = "FiberConfig2 (?)",
    -- the rest here are copied from balor sender.py, couldn't be bothered to double check them
    [0x0031] = "LockInputPort",
    [0x0036] = "GetUserData",
    [0x0037] = "GetFlyPulseCount",
    [0x0038] = "GetFlySpeed",
    [0x0040] = "IsLiteVersion",
    [0x0041] = "GetMarkTime",
}

buffer_opcodes = {
    [0x800d] = "listJumpTo",
    [0x8001] = "listJumpTo",
    [0x8005] = "listMarkTo",
    [0x8003] = "listLaserOnPoint",
    [0x8006] = "listJumpSpeed",
    [0x800c] = "listMarkSpeed",
    [0x801b] = "listMarkFreq",
    [0x8013] = "listMarkFreq",
    [0x800a] = "listMarkFreq",
    [0x8012] = "listMarkPowerRatio",
    [0x800b] = "listMarkPulseWidth",
    [0x8026] = "listIPGYLPMPulseWidth",
    [0x8007] = "listLaserOnDelay",
    [0x8008] = "listLaserOffDelay",
    [0x800f] = "listPolygonDelay",
    [0x8004] = "listDelayTime",
    [0x801a] = "listFlyEnable",
    [0x801d] = "listFlyDelay",
    [0x8011] = "listWritrPort",
    [0x8051] = "ReadyMark",
    [0x8002] = "Run",
    [0x801c] = "listDirectLaserSwitch",
    [0x801e] = "SetCo2FPK",
    [0x801f] = "lsFlyWaitInput",
    [0x8021] = "listIPGOpenMO",
    [0x8023] = "listChangeMarkCount",
    [0x8022] = "listWaitForInput",
    [0x8028] = "listFlyEncoderCount",
    [0x8029] = "listSetDaZWord",
    [0x8050] = "listJptSetParam",
    [0x8025] = "listEnableWeldPowerWave",
    [0x8024] = "listSetWeldPowerWave",
}
