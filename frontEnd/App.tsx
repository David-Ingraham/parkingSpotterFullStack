// App.tsx
import React from 'react';
import { Text, StyleSheet, Platform, View, ScrollView } from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { HomeScreen } from './screens/HomeScreen';
import { DirectSearchScreen } from './screens/DirectSearchScreen';
import { NearestParkingScreen } from './screens/NearestParkingScreen';

const Stack = createStackNavigator();

// Error Boundary Component
class ErrorBoundary extends React.Component<
  { children: React.ReactNode },
  { hasError: boolean; error: Error | null; errorInfo: any }
> {
  constructor(props: { children: React.ReactNode }) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true };
  }

  componentDidCatch(error: Error, errorInfo: any) {
    // Only log in development
    if (__DEV__) {
      console.log('Error Boundary caught an error:', error);
      console.log('Error Info:', errorInfo);
    }
    this.setState({
      error: error,
      errorInfo: errorInfo
    });
  }

  render() {
    if (this.state.hasError) {
      return (
        <View style={styles.errorContainer}>
          <ScrollView style={styles.errorScroll}>
            <Text style={styles.errorTitle}>App Error</Text>
            <Text style={styles.errorText}>Something went wrong!</Text>
            {this.state.error && (
              <View style={styles.errorDetails}>
                <Text style={styles.errorLabel}>Error:</Text>
                <Text style={styles.errorMessage}>{this.state.error.toString()}</Text>
                <Text style={styles.errorLabel}>Stack:</Text>
                <Text style={styles.errorMessage}>{this.state.error.stack}</Text>
              </View>
            )}
          </ScrollView>
        </View>
      );
    }

    return this.props.children;
  }
}

// Custom gradient-style header title component
const GradientHeaderTitle = ({ title }: { title: string }) => (
  <Text style={styles.gradientHeaderText}>{title}</Text>
);

export default function App() {
  try {
    return (
      <ErrorBoundary>
        <NavigationContainer>
          <Stack.Navigator
            screenOptions={{
              headerStyle: {
                backgroundColor: '#1a0025',
                elevation: 8,
                shadowColor: '#8B5FBF',
                shadowOffset: { width: 0, height: 4 },
                shadowOpacity: 0.3,
                shadowRadius: 8,
              },
              headerTintColor: '#fff',
            }}
          >
            <Stack.Screen 
              name="Home" 
              component={HomeScreen}
              options={{ 
                headerTitle: () => <GradientHeaderTitle title="Parking Spotter" />
              }}
            />
            <Stack.Screen 
              name="DirectSearch" 
              component={DirectSearchScreen}
              options={{ 
                headerTitle: () => <GradientHeaderTitle title="Search Cameras" />
              }}
            />
            <Stack.Screen 
              name="NearestParking" 
              component={NearestParkingScreen}
              options={{ 
                headerTitle: () => <GradientHeaderTitle title="Nearest Parking" />
              }}
            />
          </Stack.Navigator>
        </NavigationContainer>
      </ErrorBoundary>
    );
  } catch (error) {
    console.error('Error in App component:', error);
    return (
      <View style={styles.errorContainer}>
        <Text style={styles.errorTitle}>Startup Error</Text>
        <Text style={styles.errorText}>Failed to initialize app: {String(error)}</Text>
      </View>
    );
  }
}

const styles = StyleSheet.create({
  gradientHeaderText: {
    fontSize: 18,
    fontWeight: '900',
    fontFamily: Platform.OS === 'ios' ? 'Courier New' : 'monospace',
    color: '#FFB366',
    textShadowColor: '#8B5FBF',
    textShadowOffset: { width: -1, height: 2 },
    textShadowRadius: 6,
    letterSpacing: 2,
    textTransform: 'uppercase',
    transform: [{ skewX: '-3deg' }],
  },
  errorContainer: {
    flex: 1,
    backgroundColor: '#1a0025',
    padding: 20,
    justifyContent: 'center',
  },
  errorScroll: {
    flex: 1,
  },
  errorTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#FFB366',
    marginBottom: 20,
    textAlign: 'center',
  },
  errorText: {
    fontSize: 16,
    color: '#fff',
    marginBottom: 20,
    textAlign: 'center',
  },
  errorDetails: {
    backgroundColor: 'rgba(255, 255, 255, 0.1)',
    padding: 15,
    borderRadius: 8,
    marginTop: 20,
  },
  errorLabel: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#FFB366',
    marginTop: 10,
    marginBottom: 5,
  },
  errorMessage: {
    fontSize: 12,
    color: '#fff',
    fontFamily: Platform.OS === 'ios' ? 'Courier New' : 'monospace',
  },
});