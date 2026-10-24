export interface Plant {
  id: string
  name: string
  location: string
  timezone: string
  currentShift: string
}

export interface UserProfile {
  name: string
  email: string
  role: string
  initials: string
}

export interface Workspace {
  plants: Plant[]
  defaultPlantId: string
  user: UserProfile
}
