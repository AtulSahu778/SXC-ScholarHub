import { MongoClient } from 'mongodb'
import { v4 as uuidv4 } from 'uuid'
import { NextResponse } from 'next/server'

// MongoDB connection
let client
let db

async function connectToMongo() {
  if (!client) {
    client = new MongoClient(process.env.MONGO_URL)
    await client.connect()
    db = client.db(process.env.DB_NAME)
  }
  return db
}

// Helper function to handle CORS
function handleCORS(response) {
  response.headers.set('Access-Control-Allow-Origin', '*')
  response.headers.set('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
  response.headers.set('Access-Control-Allow-Headers', 'Content-Type, Authorization')
  response.headers.set('Access-Control-Allow-Credentials', 'true')
  return response
}

// Simple JWT-like token generation (for demo purposes)
function generateToken(userId) {
  return Buffer.from(JSON.stringify({ userId, exp: Date.now() + 24 * 60 * 60 * 1000 })).toString('base64')
}

function verifyToken(token) {
  try {
    const decoded = JSON.parse(Buffer.from(token, 'base64').toString())
    if (decoded.exp > Date.now()) {
      return decoded
    }
  } catch (error) {
    return null
  }
  return null
}

// Simple password hashing (for demo purposes - use bcrypt in production)
function hashPassword(password) {
  return Buffer.from(password).toString('base64')
}

function comparePassword(password, hash) {
  return Buffer.from(password).toString('base64') === hash
}

// OPTIONS handler for CORS
export async function OPTIONS() {
  return handleCORS(new NextResponse(null, { status: 200 }))
}

// Route handler function
async function handleRoute(request, { params }) {
  const { path = [] } = params
  const route = `/${path.join('/')}`
  const method = request.method

  try {
    const db = await connectToMongo()

    // Root endpoint - GET /api/
    if (route === '/' && method === 'GET') {
      return handleCORS(NextResponse.json({ message: "SXC ScholarHub API is running" }))
    }

    // Authentication endpoints
    if (route === '/auth/register' && method === 'POST') {
      const { email, password, name, department, year, role } = await request.json()
      
      if (!email || !password || !name || !department || !year) {
        return handleCORS(NextResponse.json(
          { error: "All fields are required" }, 
          { status: 400 }
        ))
      }

      // Check if user already exists
      const existingUser = await db.collection('users').findOne({ email })
      if (existingUser) {
        return handleCORS(NextResponse.json(
          { error: "User already exists" }, 
          { status: 400 }
        ))
      }

      // Determine user role - default to student, allow admin for specific emails or if explicitly set
      let userRole = 'student'
      if (role === 'admin' || email.includes('admin') || email.includes('faculty')) {
        userRole = 'admin'
      }

      const user = {
        id: uuidv4(),
        email,
        password: hashPassword(password),
        name,
        department,
        year,
        role: userRole,
        createdAt: new Date().toISOString()
      }

      await db.collection('users').insertOne(user)
      
      const token = generateToken(user.id)
      const { password: _, ...userWithoutPassword } = user
      
      return handleCORS(NextResponse.json({ 
        user: userWithoutPassword, 
        token 
      }))
    }

    if (route === '/auth/login' && method === 'POST') {
      const { email, password } = await request.json()
      
      if (!email || !password) {
        return handleCORS(NextResponse.json(
          { error: "Email and password are required" }, 
          { status: 400 }
        ))
      }

      const user = await db.collection('users').findOne({ email })
      if (!user || !comparePassword(password, user.password)) {
        return handleCORS(NextResponse.json(
          { error: "Invalid email or password" }, 
          { status: 401 }
        ))
      }

      const token = generateToken(user.id)
      const { password: _, ...userWithoutPassword } = user
      
      return handleCORS(NextResponse.json({ 
        user: userWithoutPassword, 
        token 
      }))
    }

    if (route === '/auth/verify' && method === 'GET') {
      const authHeader = request.headers.get('Authorization')
      if (!authHeader || !authHeader.startsWith('Bearer ')) {
        return handleCORS(NextResponse.json(
          { error: "No token provided" }, 
          { status: 401 }
        ))
      }

      const token = authHeader.substring(7)
      const decoded = verifyToken(token)
      
      if (!decoded) {
        return handleCORS(NextResponse.json(
          { error: "Invalid token" }, 
          { status: 401 }
        ))
      }

      // Ensure we have db connection
      const database = await connectToMongo()
      const user = await database.collection('users').findOne({ id: decoded.userId })
      if (!user) {
        return handleCORS(NextResponse.json(
          { error: "User not found" }, 
          { status: 404 }
        ))
      }

      const { password: _, ...userWithoutPassword } = user
      return handleCORS(NextResponse.json({ user: userWithoutPassword }))
    }

    // Resources endpoints
    if (route === '/resources' && method === 'GET') {
      const resources = await db.collection('resources')
        .find({})
        .sort({ uploadedAt: -1 })
        .limit(1000)
        .toArray()

      // Remove MongoDB's _id field from response
      const cleanedResources = resources.map(({ _id, ...rest }) => rest)
      
      return handleCORS(NextResponse.json(cleanedResources))
    }

    if (route === '/resources' && method === 'POST') {
      // Check authentication
      const authHeader = request.headers.get('Authorization')
      if (!authHeader || !authHeader.startsWith('Bearer ')) {
        return handleCORS(NextResponse.json(
          { error: "Authentication required" }, 
          { status: 401 }
        ))
      }

      const token = authHeader.substring(7)
      const decoded = verifyToken(token)
      
      if (!decoded) {
        return handleCORS(NextResponse.json(
          { error: "Invalid token" }, 
          { status: 401 }
        ))
      }

      const user = await db.collection('users').findOne({ id: decoded.userId })
      if (!user) {
        return handleCORS(NextResponse.json(
          { error: "User not found" }, 
          { status: 404 }
        ))
      }

      // Check if user is admin
      if (user.role !== 'admin') {
        return handleCORS(NextResponse.json(
          { error: "Only administrators can upload resources" }, 
          { status: 403 }
        ))
      }

      const resourceData = await request.json()
      
      if (!resourceData.title || !resourceData.department || !resourceData.year || !resourceData.type) {
        return handleCORS(NextResponse.json(
          { error: "Required fields are missing" }, 
          { status: 400 }
        ))
      }

      const resource = {
        id: uuidv4(),
        ...resourceData,
        uploadedBy: user.id,
        uploadedByName: user.name,
        createdAt: new Date().toISOString()
      }

      await db.collection('resources').insertOne(resource)
      
      return handleCORS(NextResponse.json(resource))
    }

    if (route.startsWith('/resources/') && method === 'GET') {
      const resourceId = route.split('/')[2]
      const resource = await db.collection('resources').findOne({ id: resourceId })
      
      if (!resource) {
        return handleCORS(NextResponse.json(
          { error: "Resource not found" }, 
          { status: 404 }
        ))
      }

      const { _id, ...cleanedResource } = resource
      return handleCORS(NextResponse.json(cleanedResource))
    }

    if (route.startsWith('/resources/') && method === 'DELETE') {
      const resourceId = route.split('/')[2]
      const result = await db.collection('resources').deleteOne({ id: resourceId })
      
      if (result.deletedCount === 0) {
        return handleCORS(NextResponse.json(
          { error: "Resource not found" }, 
          { status: 404 }
        ))
      }

      return handleCORS(NextResponse.json({ message: "Resource deleted successfully" }))
    }

    // Users endpoints (for admin)
    if (route === '/users' && method === 'GET') {
      const users = await db.collection('users')
        .find({})
        .project({ password: 0 }) // Exclude password field
        .limit(1000)
        .toArray()

      const cleanedUsers = users.map(({ _id, ...rest }) => rest)
      
      return handleCORS(NextResponse.json(cleanedUsers))
    }

    // Search endpoint
    if (route === '/search' && method === 'GET') {
      const url = new URL(request.url)
      const query = url.searchParams.get('q')
      const department = url.searchParams.get('department')
      const year = url.searchParams.get('year')
      const type = url.searchParams.get('type')

      let searchQuery = {}
      
      if (query) {
        searchQuery.$or = [
          { title: { $regex: query, $options: 'i' } },
          { description: { $regex: query, $options: 'i' } },
          { subject: { $regex: query, $options: 'i' } }
        ]
      }
      
      if (department) searchQuery.department = department
      if (year) searchQuery.year = year
      if (type) searchQuery.type = type

      const resources = await db.collection('resources')
        .find(searchQuery)
        .sort({ uploadedAt: -1 })
        .limit(100)
        .toArray()

      const cleanedResources = resources.map(({ _id, ...rest }) => rest)
      
      return handleCORS(NextResponse.json(cleanedResources))
    }

    // Route not found
    return handleCORS(NextResponse.json(
      { error: `Route ${route} not found` }, 
      { status: 404 }
    ))

  } catch (error) {
    console.error('API Error:', error)
    return handleCORS(NextResponse.json(
      { error: "Internal server error" }, 
      { status: 500 }
    ))
  }
}

// Export all HTTP methods
export const GET = handleRoute
export const POST = handleRoute
export const PUT = handleRoute
export const DELETE = handleRoute
export const PATCH = handleRoute