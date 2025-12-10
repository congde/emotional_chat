#!/usr/bin/env pwsh
# PowerShell script equivalent to 'make run'
# Runs the backend service with automatic knowledge base setup

Write-Host "🚀 启动情感聊天机器人后端服务..." -ForegroundColor Green

# Get the script directory (project root)
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

# Run the backend
python run_backend.py

