'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { BookOpen, Upload, Search, Users, FileText, GraduationCap, Download, Star, Filter, Plus, User, LogOut } from 'lucide-react'

export default function App() {
  const [user, setUser] = useState(null)
  const [resources, setResources] = useState([])
  const [filteredResources, setFilteredResources] = useState([])
  const [loading, setLoading] = useState(false)
  const [alert, setAlert] = useState(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [filterDepartment, setFilterDepartment] = useState('all')
  const [filterYear, setFilterYear] = useState('all')
  const [filterType, setFilterType] = useState('all')
  const [showUploadModal, setShowUploadModal] = useState(false)
  const [showLoginModal, setShowLoginModal] = useState(false)
  const [isLogin, setIsLogin] = useState(true)

  const departments = ['Computer Science', 'Mathematics', 'Physics', 'Chemistry', 'Biology', 'English', 'History', 'Economics']
  const years = ['First Year', 'Second Year', 'Third Year']
  const resourceTypes = ['Notes', 'Previous Year Papers', 'Syllabus', 'Assignments', 'Lab Manual']

  useEffect(() => {
    fetchResources()
  }, [])

  useEffect(() => {
    filterResources()
  }, [resources, searchTerm, filterDepartment, filterYear, filterType])

  const fetchResources = async () => {
    try {
      const response = await fetch('/api/resources')
      if (response.ok) {
        const data = await response.json()
        setResources(data)
      }
    } catch (error) {
      console.error('Error fetching resources:', error)
    }
  }

  const filterResources = () => {
    let filtered = resources.filter(resource => {
      const matchesSearch = resource.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           resource.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           resource.subject.toLowerCase().includes(searchTerm.toLowerCase())
      const matchesDepartment = filterDepartment === 'all' || resource.department === filterDepartment
      const matchesYear = filterYear === 'all' || resource.year === filterYear
      const matchesType = filterType === 'all' || resource.type === filterType
      
      return matchesSearch && matchesDepartment && matchesYear && matchesType
    })
    setFilteredResources(filtered)
  }

  const handleLogin = async (e) => {
    e.preventDefault()
    setLoading(true)
    const formData = new FormData(e.target)
    const email = formData.get('email')
    const password = formData.get('password')

    try {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      })

      const data = await response.json()
      if (response.ok) {
        setUser(data.user)
        setShowLoginModal(false)
        setAlert({ type: 'success', message: 'Login successful!' })
        localStorage.setItem('token', data.token)
      } else {
        setAlert({ type: 'error', message: data.error || 'Login failed' })
      }
    } catch (error) {
      setAlert({ type: 'error', message: 'Network error. Please try again.' })
    } finally {
      setLoading(false)
    }
  }

  const handleRegister = async (e) => {
    e.preventDefault()
    setLoading(true)
    const formData = new FormData(e.target)
    const email = formData.get('email')
    const password = formData.get('password')
    const name = formData.get('name')
    const department = formData.get('department')
    const year = formData.get('year')
    const role = formData.get('role')

    try {
      const response = await fetch('/api/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password, name, department, year, role })
      })

      const data = await response.json()
      if (response.ok) {
        setUser(data.user)
        setShowLoginModal(false)
        setAlert({ type: 'success', message: 'Registration successful!' })
        localStorage.setItem('token', data.token)
      } else {
        setAlert({ type: 'error', message: data.error || 'Registration failed' })
      }
    } catch (error) {
      setAlert({ type: 'error', message: 'Network error. Please try again.' })
    } finally {
      setLoading(false)
    }
  }

  const handleUpload = async (e) => {
    e.preventDefault()
    if (!user) {
      setAlert({ type: 'error', message: 'Please login to upload resources' })
      return
    }

    if (user.role !== 'admin') {
      setAlert({ type: 'error', message: 'Only administrators can upload resources' })
      return
    }

    setLoading(true)
    const formData = new FormData(e.target)
    const file = formData.get('file')
    
    if (!file) {
      setAlert({ type: 'error', message: 'Please select a file to upload' })
      setLoading(false)
      return
    }

    // Convert file to base64
    const reader = new FileReader()
    reader.onload = async (e) => {
      try {
        const resourceData = {
          title: formData.get('title'),
          description: formData.get('description'),
          subject: formData.get('subject'),
          department: formData.get('department'),
          year: formData.get('year'),
          type: formData.get('type'),
          fileContent: e.target.result,
          fileName: file.name,
          fileType: file.type,
          uploadedAt: new Date().toISOString()
        }

        const token = localStorage.getItem('token')
        const response = await fetch('/api/resources', {
          method: 'POST',
          headers: { 
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify(resourceData)
        })

        const data = await response.json()
        if (response.ok) {
          setAlert({ type: 'success', message: 'Resource uploaded successfully!' })
          setShowUploadModal(false)
          fetchResources()
          e.target.reset()
        } else {
          setAlert({ type: 'error', message: data.error || 'Upload failed' })
        }
      } catch (error) {
        setAlert({ type: 'error', message: 'Upload failed. Please try again.' })
      } finally {
        setLoading(false)
      }
    }
    reader.readAsDataURL(file)
  }

  const handleDownload = (resource) => {
    if (!resource.fileContent) {
      setAlert({ type: 'error', message: 'File content not available' })
      return
    }

    const link = document.createElement('a')
    link.href = resource.fileContent
    link.download = resource.fileName
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  const handleLogout = () => {
    setUser(null)
    localStorage.removeItem('token')
    setAlert({ type: 'success', message: 'Logged out successfully' })
  }

  // Check for existing token on component mount
  useEffect(() => {
    const token = localStorage.getItem('token')
    if (token) {
      // Verify token and get user info
      fetch('/api/auth/verify', {
        headers: { 'Authorization': `Bearer ${token}` }
      }).then(res => res.json()).then(data => {
        if (data.user) {
          setUser(data.user)
        }
      }).catch(() => {
        localStorage.removeItem('token')
      })
    }
  }, [])

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <GraduationCap className="h-8 w-8 text-blue-600" />
              <div>
                <h1 className="text-2xl font-bold text-gray-900">SXC ScholarHub</h1>
                <p className="text-sm text-gray-600">St. Xavier's College Academic Resources</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              {user ? (
                <>
                  <div className="flex items-center space-x-2">
                    <User className="h-4 w-4" />
                    <span className="text-sm font-medium">{user.name}</span>
                    <Badge variant="secondary">{user.role}</Badge>
                  </div>
                  <Button variant="outline" size="sm" onClick={handleLogout}>
                    <LogOut className="h-4 w-4 mr-2" />
                    Logout
                  </Button>
                </>
              ) : (
                <Button onClick={() => setShowLoginModal(true)}>
                  <User className="h-4 w-4 mr-2" />
                  Login
                </Button>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Alert */}
      {alert && (
        <div className="container mx-auto px-4 pt-4">
          <Alert className={`${alert.type === 'error' ? 'bg-red-50 border-red-200' : 'bg-green-50 border-green-200'}`}>
            <AlertDescription className={alert.type === 'error' ? 'text-red-800' : 'text-green-800'}>
              {alert.message}
            </AlertDescription>
          </Alert>
        </div>
      )}

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold text-gray-900 mb-4">
            Your Academic Resources Hub
          </h2>
          <p className="text-xl text-gray-600 mb-8">
            Centralized platform for study materials, previous year papers, and academic assistance
          </p>
          <div className="flex justify-center space-x-4">
            {user && user.role === 'admin' && (
              <Dialog open={showUploadModal} onOpenChange={setShowUploadModal}>
                <DialogTrigger asChild>
                  <Button size="lg" className="bg-blue-600 hover:bg-blue-700">
                    <Upload className="h-5 w-5 mr-2" />
                    Upload Resource
                  </Button>
                </DialogTrigger>
              </Dialog>
            )}
            <Button variant="outline" size="lg">
              <BookOpen className="h-5 w-5 mr-2" />
              Browse Resources
            </Button>
          </div>
        </div>

        {/* Search and Filter Section */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-8">
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            <div className="md:col-span-2">
              <Label htmlFor="search">Search Resources</Label>
              <div className="relative">
                <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                <Input
                  id="search"
                  placeholder="Search by title, subject, or description..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            <div>
              <Label htmlFor="department">Department</Label>
              <Select value={filterDepartment} onValueChange={setFilterDepartment}>
                <SelectTrigger>
                  <SelectValue placeholder="All Departments" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Departments</SelectItem>
                  {departments.map(dept => (
                    <SelectItem key={dept} value={dept}>{dept}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label htmlFor="year">Year</Label>
              <Select value={filterYear} onValueChange={setFilterYear}>
                <SelectTrigger>
                  <SelectValue placeholder="All Years" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Years</SelectItem>
                  {years.map(year => (
                    <SelectItem key={year} value={year}>{year}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label htmlFor="type">Type</Label>
              <Select value={filterType} onValueChange={setFilterType}>
                <SelectTrigger>
                  <SelectValue placeholder="All Types" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Types</SelectItem>
                  {resourceTypes.map(type => (
                    <SelectItem key={type} value={type}>{type}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
        </div>

        {/* Resources Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredResources.map((resource) => (
            <Card key={resource.id} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex justify-between items-start">
                  <div>
                    <CardTitle className="text-lg">{resource.title}</CardTitle>
                    <CardDescription>{resource.subject}</CardDescription>
                  </div>
                  <Badge variant="outline">{resource.type}</Badge>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-gray-600 mb-4">{resource.description}</p>
                <div className="flex flex-wrap gap-2 mb-4">
                  <Badge variant="secondary">{resource.department}</Badge>
                  <Badge variant="secondary">{resource.year}</Badge>
                </div>
                <div className="flex justify-between items-center">
                  <div className="text-xs text-gray-500">
                    {new Date(resource.uploadedAt).toLocaleDateString()}
                  </div>
                  <Button
                    size="sm"
                    onClick={() => handleDownload(resource)}
                    className="bg-green-600 hover:bg-green-700"
                  >
                    <Download className="h-4 w-4 mr-2" />
                    Download
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {filteredResources.length === 0 && (
          <div className="text-center py-12">
            <FileText className="h-16 w-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No resources found</h3>
            <p className="text-gray-500">Try adjusting your search criteria or upload new resources.</p>
          </div>
        )}
      </main>

      {/* Upload Modal */}
      <Dialog open={showUploadModal} onOpenChange={setShowUploadModal}>
        <DialogContent className="sm:max-w-[500px]">
          <DialogHeader>
            <DialogTitle>Upload Academic Resource</DialogTitle>
            <DialogDescription>
              Share your study materials with fellow students at SXC
            </DialogDescription>
          </DialogHeader>
          <form onSubmit={handleUpload} className="space-y-4">
            <div>
              <Label htmlFor="title">Title</Label>
              <Input id="title" name="title" placeholder="e.g., Data Structures Notes" required />
            </div>
            <div>
              <Label htmlFor="description">Description</Label>
              <Textarea id="description" name="description" placeholder="Brief description of the resource" />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="subject">Subject</Label>
                <Input id="subject" name="subject" placeholder="e.g., Computer Science" required />
              </div>
              <div>
                <Label htmlFor="department">Department</Label>
                <Select name="department" required>
                  <SelectTrigger>
                    <SelectValue placeholder="Select Department" />
                  </SelectTrigger>
                  <SelectContent>
                    {departments.map(dept => (
                      <SelectItem key={dept} value={dept}>{dept}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="year">Year</Label>
                <Select name="year" required>
                  <SelectTrigger>
                    <SelectValue placeholder="Select Year" />
                  </SelectTrigger>
                  <SelectContent>
                    {years.map(year => (
                      <SelectItem key={year} value={year}>{year}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label htmlFor="type">Type</Label>
                <Select name="type" required>
                  <SelectTrigger>
                    <SelectValue placeholder="Select Type" />
                  </SelectTrigger>
                  <SelectContent>
                    {resourceTypes.map(type => (
                      <SelectItem key={type} value={type}>{type}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div>
              <Label htmlFor="file">File</Label>
              <Input id="file" name="file" type="file" accept=".pdf,.doc,.docx,.ppt,.pptx" required />
            </div>
            <div className="flex justify-end space-x-2">
              <Button type="button" variant="outline" onClick={() => setShowUploadModal(false)}>
                Cancel
              </Button>
              <Button type="submit" disabled={loading}>
                {loading ? 'Uploading...' : 'Upload Resource'}
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>

      {/* Login/Register Modal */}
      <Dialog open={showLoginModal} onOpenChange={setShowLoginModal}>
        <DialogContent className="sm:max-w-[400px]">
          <DialogHeader>
            <DialogTitle>{isLogin ? 'Login' : 'Register'} to SXC ScholarHub</DialogTitle>
            <DialogDescription>
              {isLogin ? 'Sign in to your account' : 'Create a new account'}
            </DialogDescription>
          </DialogHeader>
          <Tabs value={isLogin ? 'login' : 'register'} onValueChange={(value) => setIsLogin(value === 'login')}>
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="login">Login</TabsTrigger>
              <TabsTrigger value="register">Register</TabsTrigger>
            </TabsList>
            <TabsContent value="login">
              <form onSubmit={handleLogin} className="space-y-4">
                <div>
                  <Label htmlFor="email">Email</Label>
                  <Input id="email" name="email" type="email" required />
                </div>
                <div>
                  <Label htmlFor="password">Password</Label>
                  <Input id="password" name="password" type="password" required />
                </div>
                <Button type="submit" className="w-full" disabled={loading}>
                  {loading ? 'Logging in...' : 'Login'}
                </Button>
              </form>
            </TabsContent>
            <TabsContent value="register">
              <form onSubmit={handleRegister} className="space-y-4">
                <div>
                  <Label htmlFor="name">Full Name</Label>
                  <Input id="name" name="name" required />
                </div>
                <div>
                  <Label htmlFor="email">Email</Label>
                  <Input id="email" name="email" type="email" required />
                </div>
                <div>
                  <Label htmlFor="password">Password</Label>
                  <Input id="password" name="password" type="password" required />
                </div>
                <div>
                  <Label htmlFor="department">Department</Label>
                  <Select name="department" required>
                    <SelectTrigger>
                      <SelectValue placeholder="Select Department" />
                    </SelectTrigger>
                    <SelectContent>
                      {departments.map(dept => (
                        <SelectItem key={dept} value={dept}>{dept}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label htmlFor="year">Year</Label>
                  <Select name="year" required>
                    <SelectTrigger>
                      <SelectValue placeholder="Select Year" />
                    </SelectTrigger>
                    <SelectContent>
                      {years.map(year => (
                        <SelectItem key={year} value={year}>{year}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <Button type="submit" className="w-full" disabled={loading}>
                  {loading ? 'Creating Account...' : 'Create Account'}
                </Button>
              </form>
            </TabsContent>
          </Tabs>
        </DialogContent>
      </Dialog>
    </div>
  )
}