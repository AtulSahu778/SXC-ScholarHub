import { MongoClient } from 'mongodb'
import { v4 as uuidv4 } from 'uuid'
import { NextResponse } from 'next/server'

// MongoDB connection
let client
let db

async function connectToMongo() {
  if (!client) {
    try {
      console.log('Connecting to MongoDB...')
      
      // Check for environment variable (support both common names)
      const mongoUrl = process.env.MONGO_URL || process.env.MONGODB_URI
      
      if (!mongoUrl) {
        throw new Error('MONGO_URL or MONGODB_URI environment variable is not set')
      }
      
      console.log('Using MongoDB URL:', mongoUrl.replace(/\/\/[^:]+:[^@]+@/, '//***:***@'))
      
      // Create client with proper options (removed deprecated options)
      client = new MongoClient(mongoUrl, {
        serverSelectionTimeoutMS: 30000, // 30 second timeout
        connectTimeoutMS: 30000,
        socketTimeoutMS: 30000,
        maxPoolSize: 10,
        retryWrites: true,
      })
      
      // Connect with timeout
      await client.connect()
      console.log('MongoDB client connected successfully')
      
      // Use the database name from env or default to 'cluster0'
      const dbName = process.env.MONGO_DATABASE || process.env.DB_NAME || 'cluster0'
      db = client.db(dbName)
      
      console.log('Successfully connected to database:', dbName)
      
      // Test the connection
      await db.admin().ping()
      console.log('Database ping successful')
      
    } catch (error) {
      console.error('MongoDB connection error:', error)
      
      // Clean up on error
      if (client) {
        try {
          await client.close()
        } catch (closeError) {
          console.error('Error closing client:', closeError)
        }
      }
      
      client = null
      db = null
      throw new Error(`Database connection failed: ${error.message}`)
    }
  }
  
  if (!db) {
    throw new Error('Database connection not established')
  }
  
  return db
}

// Add connection health check
async function checkConnection() {
  try {
    if (db) {
      await db.admin().ping()
      return true
    }
    return false
  } catch (error) {
    console.error('Connection health check failed:', error)
    // Reset connection on health check failure
    client = null
    db = null
    return false
  }
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
    console.error('Token verification error:', error)
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
    // Check connection health first
    const isHealthy = await checkConnection()
    if (!isHealthy) {
      console.log('Connection unhealthy, reconnecting...')
      client = null
      db = null
    }

    // Ensure database connection
    const database = await connectToMongo()
    
    if (!database) {
      throw new Error('Database connection failed')
    }

    // Root endpoint - GET /api/
    if (route === '/' && method === 'GET') {
      return handleCORS(NextResponse.json({ message: "SXC ScholarHub API is running" }))
    }

    // Authentication endpoints
    if (route === '/auth/register' && method === 'POST') {
      const { email, password, name, department, year } = await request.json()
      
      if (!email || !password || !name || !department || !year) {
        return handleCORS(NextResponse.json(
          { error: "All fields are required" }, 
          { status: 400 }
        ))
      }

      // Check if user already exists
      const existingUser = await database.collection('users').findOne({ email })
      if (existingUser) {
        return handleCORS(NextResponse.json(
          { error: "User already exists" }, 
          { status: 400 }
        ))
      }

      // Determine user role - only your specific email gets admin role
      let userRole = 'student'
      if (email === 'sahuatul2005@gmail.com') {
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
        downloads: 0,
        recentViews: [],
        bookmarks: [],
        createdAt: new Date().toISOString()
      }

      await database.collection('users').insertOne(user)
      
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

      const user = await database.collection('users').findOne({ email })
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
      const resources = await database.collection('resources')
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
      const authHeader = request.headers.get('Authorization');
      if (!authHeader || !authHeader.startsWith('Bearer ')) {
        return handleCORS(NextResponse.json(
          { error: "Authentication required" }, 
          { status: 401 }
        ));
      }

      const token = authHeader.substring(7);
      const decoded = verifyToken(token);
      if (!decoded) {
        return handleCORS(NextResponse.json(
          { error: "Invalid token" }, 
          { status: 401 }
        ));
      }

      const user = await database.collection('users').findOne({ id: decoded.userId });
      if (!user) {
        return handleCORS(NextResponse.json(
          { error: "User not found" }, 
          { status: 404 }
        ));
      }
      if (user.role !== 'admin') {
        return handleCORS(NextResponse.json(
          { error: "Only administrators can upload resources" }, 
          { status: 403 }
        ));
      }

      // Validate input
      let resourceData;
      try {
        resourceData = await request.json();
      } catch (err) {
        return handleCORS(NextResponse.json(
          { error: "Invalid JSON body", details: err.message }, 
          { status: 400 }
        ));
      }
      const { title, department, year, type, fileContent, gdriveLink } = resourceData;
      // Only require at least one of fileContent or gdriveLink
      if (!fileContent && !gdriveLink) {
        return handleCORS(NextResponse.json(
          { error: "Either a file or a Google Drive link is required" },
          { status: 400 }
        ));
      }
      if (fileContent && gdriveLink) {
        return handleCORS(NextResponse.json(
          { error: "Provide only one: file or Google Drive link" },
          { status: 400 }
        ));
      }
      // Prepare resource
      let fileBuffer = null;
      if (fileContent && fileContent.startsWith('data:')) {
        // Convert base64 data URL to Buffer
        const base64 = fileContent.split(',')[1];
        fileBuffer = Buffer.from(base64, 'base64');
      }
      const resource = {
        id: uuidv4(),
        ...resourceData,
        fileContent: fileBuffer || fileContent, // Store as Buffer if possible
        downloadCount: 0, // Track download count for trending
        uploadedBy: user.id,
        uploadedByName: user.name,
        uploadedAt: new Date().toISOString(),
        createdAt: new Date().toISOString()
      };
      // Insert and respond
      try {
        await database.collection('resources').insertOne(resource);
        // Only return a success message and the resource id
        return handleCORS(NextResponse.json({
          message: "Resource uploaded successfully",
          id: resource.id
        }));
      } catch (err) {
        console.error('Resource upload error:', err);
        return handleCORS(NextResponse.json(
          { error: "Failed to upload resource", details: err.message }, 
          { status: 500 }
        ));
      }
    }

    if (route.startsWith('/resources/') && method === 'GET') {
      const resourceId = route.split('/')[2]
      const resource = await database.collection('resources').findOne({ id: resourceId })
      
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
      // Check authentication for deletion
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

      const user = await database.collection('users').findOne({ id: decoded.userId })
      if (!user || user.role !== 'admin') {
        return handleCORS(NextResponse.json(
          { error: "Only administrators can delete resources" }, 
          { status: 403 }
        ))
      }

      const resourceId = route.split('/')[2]
      const result = await database.collection('resources').deleteOne({ id: resourceId })
      
      if (result.deletedCount === 0) {
        return handleCORS(NextResponse.json(
          { error: "Resource not found" }, 
          { status: 404 }
        ))
      }

      return handleCORS(NextResponse.json({ message: "Resource deleted successfully" }))
    }

    // Secure download endpoint
    if (route.startsWith('/resources/') && route.endsWith('/download') && method === 'GET') {
      // Check authentication
      const authHeader = request.headers.get('Authorization')
      if (!authHeader || !authHeader.startsWith('Bearer ')) {
        return handleCORS(new NextResponse('Authentication required', { status: 401 }))
      }
      const token = authHeader.substring(7)
      const decoded = verifyToken(token)
      if (!decoded) {
        return handleCORS(new NextResponse('Invalid token', { status: 401 }))
      }
      // Get resource ID
      const parts = route.split('/')
      const resourceId = parts[2]
      const resource = await database.collection('resources').findOne({ id: resourceId })
      if (!resource) {
        return handleCORS(new NextResponse('Resource not found', { status: 404 }))
      }
      // Extract file data (Buffer or base64 string)
      let fileBuffer
      if (Buffer.isBuffer(resource.fileContent)) {
        fileBuffer = resource.fileContent
      } else if (typeof resource.fileContent === 'string' && resource.fileContent.startsWith('data:')) {
        const base64 = resource.fileContent.split(',')[1]
        fileBuffer = Buffer.from(base64, 'base64')
      } else {
        return handleCORS(new NextResponse('File not available', { status: 404 }))
      }

      // Update user download tracking and resource download count
      const user = await database.collection('users').findOne({ id: decoded.userId })
      if (user) {
        // Update user downloads count and recent views
        let recentViews = user.recentViews || []
        recentViews = recentViews.filter(id => id !== resourceId) // Remove if already exists
        recentViews.unshift(resourceId) // Add to beginning
        recentViews = recentViews.slice(0, 5) // Keep only last 5

        await database.collection('users').updateOne(
          { id: decoded.userId },
          { 
            $inc: { downloads: 1 },
            $set: { recentViews }
          }
        )

        // Increment resource download count
        await database.collection('resources').updateOne(
          { id: resourceId },
          { $inc: { downloadCount: 1 } }
        )
      }

      const response = new NextResponse(fileBuffer, {
        status: 200,
        headers: {
          'Content-Type': resource.fileType,
          'Content-Disposition': `attachment; filename="${resource.fileName}"`,
        },
      })
      return handleCORS(response)
    }

    if (route.startsWith('/resources/') && method === 'PATCH') {
      // Check authentication for editing
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
      const user = await database.collection('users').findOne({ id: decoded.userId })
      if (!user || user.role !== 'admin') {
        return handleCORS(NextResponse.json(
          { error: "Only administrators can edit resources" }, 
          { status: 403 }
        ))
      }
      const resourceId = route.split('/')[2]
      let updateData
      try {
        updateData = await request.json()
      } catch (err) {
        return handleCORS(NextResponse.json(
          { error: "Invalid JSON body", details: err.message }, 
          { status: 400 }
        ))
      }
      // Remove fields that should not be updated directly
      delete updateData.id
      delete updateData.uploadedBy
      delete updateData.uploadedByName
      delete updateData.createdAt
      // Set updatedAt
      updateData.updatedAt = new Date().toISOString()
      const result = await database.collection('resources').findOneAndUpdate(
        { id: resourceId },
        { $set: updateData },
        { returnDocument: 'after' }
      )
      if (!result.value) {
        return handleCORS(NextResponse.json(
          { error: "Resource not found" }, 
          { status: 404 }
        ))
      }
      const { _id, ...updatedResource } = result.value
      return handleCORS(NextResponse.json(updatedResource))
    }

    // Users endpoints (for admin)
    if (route === '/users' && method === 'GET') {
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

      const user = await database.collection('users').findOne({ id: decoded.userId })
      if (!user || user.role !== 'admin') {
        return handleCORS(NextResponse.json(
          { error: "Only administrators can view users" }, 
          { status: 403 }
        ))
      }

      const users = await database.collection('users')
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

      const resources = await database.collection('resources')
        .find(searchQuery)
        .sort({ uploadedAt: -1 })
        .limit(100)
        .toArray()

      const cleanedResources = resources.map(({ _id, ...rest }) => rest)
      
      return handleCORS(NextResponse.json(cleanedResources))
    }

    // Dashboard endpoints
    if (route === '/dashboard/student' && method === 'GET') {
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

      const user = await database.collection('users').findOne({ id: decoded.userId })
      if (!user) {
        return handleCORS(NextResponse.json(
          { error: "User not found" }, 
          { status: 404 }
        ))
      }

      // Get recent resources based on user's recent views
      const recentResources = await database.collection('resources')
        .find({ id: { $in: user.recentViews || [] } })
        .limit(5)
        .toArray()

      // Get bookmarked resources
      const bookmarkedResources = await database.collection('resources')
        .find({ id: { $in: user.bookmarks || [] } })
        .limit(10)
        .toArray()

      // Get top 5 trending resources (by download count)
      const trendingResources = await database.collection('resources')
        .find({})
        .sort({ downloadCount: -1 })
        .limit(5)
        .toArray()

      // Clean MongoDB _id fields
      const cleanRecent = recentResources.map(({ _id, ...rest }) => rest)
      const cleanBookmarked = bookmarkedResources.map(({ _id, ...rest }) => rest)
      const cleanTrending = trendingResources.map(({ _id, ...rest }) => rest)

      return handleCORS(NextResponse.json({
        totalDownloads: user.downloads || 0,
        recentResources: cleanRecent,
        bookmarkedResources: cleanBookmarked,
        trendingResources: cleanTrending
      }))
    }

    if (route === '/dashboard/admin' && method === 'GET') {
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

      const user = await database.collection('users').findOne({ id: decoded.userId })
      if (!user || user.role !== 'admin') {
        return handleCORS(NextResponse.json(
          { error: "Admin access required" }, 
          { status: 403 }
        ))
      }

      // Get total uploaded resources count by this admin
      const totalUploads = await database.collection('resources').countDocuments({ uploadedBy: user.id })

      // Get last 5 uploads by this admin
      const recentUploads = await database.collection('resources')
        .find({ uploadedBy: user.id })
        .sort({ uploadedAt: -1 })
        .limit(5)
        .toArray()

      // For now, pending requests will be empty (placeholder for future feature)
      const pendingRequests = []

      // Clean MongoDB _id fields
      const cleanUploads = recentUploads.map(({ _id, ...rest }) => rest)

      return handleCORS(NextResponse.json({
        totalUploads,
        recentUploads: cleanUploads,
        pendingRequests
      }))
    }

    // Bookmark endpoints
    if (route.startsWith('/resources/') && route.endsWith('/bookmark') && method === 'POST') {
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

      const resourceId = route.split('/')[2]
      
      // Check if resource exists
      const resource = await database.collection('resources').findOne({ id: resourceId })
      if (!resource) {
        return handleCORS(NextResponse.json(
          { error: "Resource not found" }, 
          { status: 404 }
        ))
      }

      const user = await database.collection('users').findOne({ id: decoded.userId })
      if (!user) {
        return handleCORS(NextResponse.json(
          { error: "User not found" }, 
          { status: 404 }
        ))
      }

      let bookmarks = user.bookmarks || []
      let isBookmarked = bookmarks.includes(resourceId)
      
      if (isBookmarked) {
        // Remove bookmark
        bookmarks = bookmarks.filter(id => id !== resourceId)
      } else {
        // Add bookmark
        bookmarks.push(resourceId)
      }

      await database.collection('users').updateOne(
        { id: decoded.userId },
        { $set: { bookmarks } }
      )

      return handleCORS(NextResponse.json({
        isBookmarked: !isBookmarked,
        message: isBookmarked ? 'Bookmark removed' : 'Bookmark added'
      }))
    }

    // Route not found
    return handleCORS(NextResponse.json(
      { error: `Route ${route} not found` }, 
      { status: 404 }
    ))

  } catch (error) {
    console.error('API Error:', error)
    return handleCORS(NextResponse.json(
      { error: "Internal server error", details: error.message }, 
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