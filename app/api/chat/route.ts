import { NextRequest, NextResponse } from 'next/server'
import { v4 as uuidv4 } from 'uuid'

// This route uses a Python subprocess to handle Gemini API calls
// to avoid exposing the API key to the client
export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { message, sessionId } = body

    if (!message || typeof message !== 'string') {
      return NextResponse.json(
        { error: 'Message is required and must be a string' },
        { status: 400 }
      )
    }

    if (!sessionId) {
      return NextResponse.json(
        { error: 'Session ID is required' },
        { status: 400 }
      )
    }

    // Import child_process to run Python script
    const { spawn } = require('child_process')
    
    return new Promise((resolve) => {
      // Pass environment variables to subprocess
      const env = {
        ...process.env,
        GEMINI_API_KEY: process.env.GEMINI_API_KEY
      }
      
      const python = spawn('python3', ['-c', `
import sys
import json
import asyncio
import os
from emergentintegrations.llm.chat import LlmChat, UserMessage

async def chat_with_gemini():
    try:
        # Get API key from environment
        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key:
            return {"error": "API key not configured"}
        
        # Initialize chat with Gemini 2.0 Flash
        chat = LlmChat(
            api_key=api_key,
            session_id="${sessionId}",
            system_message="You are a helpful academic assistant for ScholarHub. You specialize in helping students with their academic questions, research, study tips, and educational content. Be friendly, informative, and supportive."
        ).with_model("gemini", "gemini-2.0-flash")
        
        # Create user message
        user_message = UserMessage(text="${message.replace(/"/g, '\\"')}")
        
        # Send message and get response
        response = await chat.send_message(user_message)
        
        return {"response": response}
        
    except Exception as e:
        return {"error": f"Chat error: {str(e)}"}

# Run the async function
result = asyncio.run(chat_with_gemini())
print(json.dumps(result))
`])

      let output = ''
      let errorOutput = ''

      python.stdout.on('data', (data: Buffer) => {
        output += data.toString()
      })

      python.stderr.on('data', (data: Buffer) => {
        errorOutput += data.toString()
      })

      python.on('close', (code: number) => {
        try {
          if (code !== 0) {
            console.error('Python process error:', errorOutput)
            resolve(NextResponse.json(
              { error: 'Failed to process chat request' },
              { status: 500 }
            ))
            return
          }

          const result = JSON.parse(output.trim())
          
          if (result.error) {
            console.error('Gemini API error:', result.error)
            resolve(NextResponse.json(
              { error: result.error },
              { status: 500 }
            ))
            return
          }

          resolve(NextResponse.json({
            response: result.response,
            sessionId: sessionId
          }))
        } catch (parseError) {
          console.error('Failed to parse Python output:', parseError)
          console.error('Raw output:', output)
          console.error('Error output:', errorOutput)
          
          resolve(NextResponse.json(
            { error: 'Failed to parse response' },
            { status: 500 }
          ))
        }
      })

      // Handle process errors
      python.on('error', (error: Error) => {
        console.error('Failed to start Python process:', error)
        resolve(NextResponse.json(
          { error: 'Failed to start chat service' },
          { status: 500 }
        ))
      })
    })
  } catch (error) {
    console.error('Chat API error:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}