#!/usr/bin/env bash
ectool setProperty /myParent/DeviceResource --value $(ectool getProperty "/myJobStep/assignedResourceName")