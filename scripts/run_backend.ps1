#!/usr/bin/env pwsh
# PowerShell script equivalent to 'make run'
# Runs the backend service with automatic knowledge base setup

Write-Host "🚀 启动情感聊天机器人后端服务..." -ForegroundColor Green

# Resolve the project root from scripts/.
$projectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $projectRoot

# Run the backend
python run_backend.py

