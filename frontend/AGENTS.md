# Frontend Development Guide for AI Agents

## Project Overview

This is a **Next.js 15 + React 19** quantitative trading backtesting platform
frontend with advanced patterns including TanStack Query v5 for server state
management, Hey-API auto-generated client, and Material-UI v7 component library.

## Critical Architecture Rules

### 1. Custom Hooks Pattern (Mandatory)

**ALL API interactions MUST go through domain-specific custom hooks**

```typescript
// ✅ CORRECT
import { useBacktest } from '@/hooks/useBacktests';

function MyComponent() {
  const { backtestList, createBacktest, deleteBacktest } = useBacktest();
  return <div>{backtestList?.map(...)}</div>;
}

// ❌ WRONG - Never call API services directly in components
import { BacktestService } from '@/client';
import { useQuery } from '@tanstack/react-query';

function MyComponent() {
  const { data } = useQuery({
    queryKey: ['backtests'],
    queryFn: () => BacktestService.getBacktests(),
  });
}
```

### 2. API Client Configuration

- Backend runs on **port 8500** (NOT 8000)
- Frontend expects backend at `http://localhost:8500`
- Configured in `runtimeConfig.ts`
- Client auto-generated from OpenAPI schema (DO NOT edit manually)

### 3. State Management Strategy

#### Server State (TanStack Query v5)

- Backend API data caching and synchronization
- Queries: Data fetching (auto-refetch, caching)
- Mutations: Data modification (optimistic updates)
- Managed through custom hooks

#### Client State (React Context)

- AuthContext: Authentication state, user info
- SnackbarContext: Global notifications (success/error)
- SidebarContext: UI state (sidebar expand/collapse)

#### Local State (useState/useReducer)

- Component-specific state
- Form inputs, modal open/close, tab selection, etc.

## Service Layer Structure

### Custom Hooks (Domain-Driven)

Access domain-specific data through custom hooks:

```typescript
// Hook imports
import { useBacktest } from "@/hooks/useBacktests";
import { useMarketData } from "@/hooks/useMarketData";
import { useStrategy } from "@/hooks/useStrategy";
import { useWatchList } from "@/hooks/useWatchList";
import { useCrypto } from "@/hooks/useCrypto";
import { useEconomic } from "@/hooks/useEconomic";
import { useFundamental } from "@/hooks/useFundamental";
import { useIntelligence } from "@/hooks/useIntelligence";
import { useTechnicalIndicator } from "@/hooks/useTechnicalIndicator";

// Usage pattern
const {
  // Data
  backtestList,
  backtestDetail,

  // Loading states
  isLoading,
  isError,

  // Actions
  createBacktest,
  updateBacktest,
  deleteBacktest,

  // Utilities
  refetch,
} = useBacktest();
```

### Context API

```typescript
// Authentication
import { useAuth } from "@/contexts/AuthContext";
const { user, login, logout, isAuthenticated } = useAuth();

// Notifications
import { useSnackbar } from "@/contexts/SnackbarContext";
const { showSuccess, showError, showInfo, showWarning } = useSnackbar();

// Sidebar state (only in layout components)
import { useSidebar } from "@/contexts/SidebarContext";
const { isExpanded, toggle } = useSidebar();
```

## API Development Guidelines

### 1. Creating a New Custom Hook

```typescript
// src/hooks/useExample.ts
import type { ExampleCreate, ExampleUpdate } from "@/client";
import { ExampleService } from "@/client";
import { useSnackbar } from "@/contexts/SnackbarContext";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

// Query keys for cache management
export const exampleQueryKeys = {
  all: ["example"] as const,
  lists: () => [...exampleQueryKeys.all, "list"] as const,
  list: (filters: string) =>
    [...exampleQueryKeys.lists(), { filters }] as const,
  details: () => [...exampleQueryKeys.all, "detail"] as const,
  detail: (id: string) => [...exampleQueryKeys.details(), id] as const,
};

export function useExample() {
  const queryClient = useQueryClient();
  const { showSuccess, showError } = useSnackbar();

  // Query: List
  const exampleListQuery = useQuery({
    queryKey: exampleQueryKeys.lists(),
    queryFn: async () => {
      const response = await ExampleService.getExamples();
      return response.data;
    },
    staleTime: 1000 * 60 * 5, // 5 minutes
    gcTime: 30 * 60 * 1000, // 30 minutes
  });

  // Query: Detail
  const useExampleDetail = (id: string) => {
    return useQuery({
      queryKey: exampleQueryKeys.detail(id),
      queryFn: async () => {
        const response = await ExampleService.getExample({ path: { id } });
        return response.data;
      },
      enabled: !!id,
      staleTime: 1000 * 60 * 5,
    });
  };

  // Mutation: Create
  const createMutation = useMutation({
    mutationFn: async (data: ExampleCreate) => {
      const response = await ExampleService.createExample({ body: data });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: exampleQueryKeys.lists() });
      showSuccess("생성되었습니다.");
    },
    onError: (error) => {
      showError(`생성 실패: ${error.message}`);
    },
  });

  // Mutation: Update
  const updateMutation = useMutation({
    mutationFn: async ({ id, data }: { id: string; data: ExampleUpdate }) => {
      const response = await ExampleService.updateExample({
        path: { id },
        body: data,
      });
      return response.data;
    },
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: exampleQueryKeys.detail(id) });
      queryClient.invalidateQueries({ queryKey: exampleQueryKeys.lists() });
      showSuccess("수정되었습니다.");
    },
    onError: (error) => {
      showError(`수정 실패: ${error.message}`);
    },
  });

  // Mutation: Delete
  const deleteMutation = useMutation({
    mutationFn: async (id: string) => {
      await ExampleService.deleteExample({ path: { id } });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: exampleQueryKeys.lists() });
      showSuccess("삭제되었습니다.");
    },
    onError: (error) => {
      showError(`삭제 실패: ${error.message}`);
    },
  });

  return {
    // Queries
    exampleList: exampleListQuery.data,
    isLoading: exampleListQuery.isLoading,
    isError: exampleListQuery.isError,
    error: exampleListQuery.error,
    refetch: exampleListQuery.refetch,

    // Detail hook
    useExampleDetail,

    // Mutations
    createExample: createMutation.mutateAsync,
    isCreating: createMutation.isPending,
    updateExample: updateMutation.mutateAsync,
    isUpdating: updateMutation.isPending,
    deleteExample: deleteMutation.mutateAsync,
    isDeleting: deleteMutation.isPending,
  };
}
```

### 2. Component Pattern

```typescript
// src/components/examples/ExampleList.tsx
'use client';

import { useExample } from '@/hooks/useExample';
import { Button, CircularProgress } from '@mui/material';

export default function ExampleList() {
  const {
    exampleList,
    isLoading,
    isError,
    error,
    deleteExample,
    isDeleting,
  } = useExample();

  if (isLoading) return <CircularProgress />;
  if (isError) return <div>Error: {error.message}</div>;

  const handleDelete = async (id: string) => {
    if (confirm('정말 삭제하시겠습니까?')) {
      await deleteExample(id);
    }
  };

  return (
    <div>
      {exampleList?.map((item) => (
        <div key={item.id}>
          <span>{item.name}</span>
          <Button
            onClick={() => handleDelete(item.id)}
            disabled={isDeleting}
          >
            삭제
          </Button>
        </div>
      ))}
    </div>
  );
}
```

### 3. Next.js 15 Async Params Pattern

```typescript
// src/app/(main)/examples/[id]/page.tsx
import { use } from 'react';

interface PageProps {
  params: Promise<{ id: string }>;
}

export default function ExampleDetailPage(props: PageProps) {
  // Next.js 15: params is a Promise, must unwrap
  const params = use(props.params);
  const id = params.id;

  const { useExampleDetail } = useExample();
  const { data: example, isLoading } = useExampleDetail(id);

  if (isLoading) return <CircularProgress />;

  return <div>{example?.name}</div>;
}
```

## Component Organization

### Layout Hierarchy

```
RootLayout (app/layout.tsx)
  ├─ Global Providers (Query, Auth, Snackbar, Theme)
  └─ Children
      ├─ (auth) routes → Public pages
      └─ (main) routes → MainLayout
          ├─ Sidebar + Header
          ├─ DialogsProvider
          ├─ NotificationsProvider
          └─ Page Content
```

### Component Structure

```
components/
├─ auth/              # Authentication UI
├─ backtests/         # Backtest-specific components
├─ common/            # Shared components (Logo, LoadingSpinner)
├─ dashboard/         # Dashboard widgets
├─ layout/            # Layout components (Header, Sidebar, PageContainer)
├─ market-data/       # Market data visualization (Charts, Indicators)
├─ providers/         # Context providers (QueryProvider)
├─ shared-theme/      # Theme system (AppTheme, ColorModeSelect)
└─ strategies/        # Strategy management components
```

## Common Tasks

### Adding a New Page

```bash
# 1. Create route directory
mkdir -p src/app/(main)/new-page

# 2. Create page.tsx
cat > src/app/(main)/new-page/page.tsx << 'EOF'
'use client';

import PageContainer from '@/components/layout/PageContainer';

export default function NewPage() {
  return (
    <PageContainer title="New Page" description="Description">
      {/* Page content */}
    </PageContainer>
  );
}
EOF

# 3. Add to sidebar navigation (if needed)
# Edit: src/components/layout/sidebar/Sidebar.tsx
```

### Adding a New Domain Hook

1. **Check if backend endpoint exists** (OpenAPI schema)
2. **Regenerate client** if backend schema changed: `pnpm gen:client`
3. **Create hook** in `src/hooks/useNewDomain.ts`
4. **Follow pattern** from existing hooks (useBacktest, useMarketData)
5. **Export and use** in components

### Adding a Context

```typescript
// src/contexts/NewContext.tsx
'use client';

import { createContext, useContext, useState } from 'react';

interface NewContextType {
  value: string;
  setValue: (value: string) => void;
}

const NewContext = createContext<NewContextType | undefined>(undefined);

export function NewProvider({ children }: { children: React.ReactNode }) {
  const [value, setValue] = useState('');

  return (
    <NewContext.Provider value={{ value, setValue }}>
      {children}
    </NewContext.Provider>
  );
}

export function useNew() {
  const context = useContext(NewContext);
  if (!context) {
    throw new Error('useNew must be used within NewProvider');
  }
  return context;
}
```

### Regenerating API Client

```bash
# MUST run when backend OpenAPI schema changes
pnpm gen:client

# Or directly
./scripts/generate-client.sh

# What happens:
# 1. Downloads openapi.json from http://localhost:8500/openapi.json
# 2. Saves to frontend/src/openapi.json
# 3. Generates TypeScript client via Hey-API
# 4. Creates files in frontend/src/client/
#    - sdk.gen.ts (Service classes)
#    - types.gen.ts (TypeScript types)
#    - client.ts (HTTP client config)
```

## Material-UI Patterns

### Theme Customization

```typescript
// src/components/shared-theme/customizations/inputs.tsx
export const inputsCustomizations = {
  MuiButton: {
    styleOverrides: {
      root: ({ theme, ownerState }) => ({
        borderRadius: theme.shape.borderRadius,
        textTransform: "none",
        ...(ownerState.variant === "contained" && {
          backgroundColor: theme.palette.primary.main,
        }),
      }),
    },
  },
};
```

### Using MUI Components

```typescript
import {
  Button,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';

function MyDialog({ open, onClose }) {
  return (
    <Dialog open={open} onClose={onClose}>
      <DialogTitle>Title</DialogTitle>
      <DialogContent>
        <TextField label="Input" fullWidth />
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button variant="contained">Confirm</Button>
      </DialogActions>
    </Dialog>
  );
}
```

## Chart Components

### LightWeightChart (Recommended for Simple Charts)

```typescript
import LightWeightChart from '@/components/market-data/LightWeightChart';

<LightWeightChart
  data={chartData}
  symbol="AAPL"
  chartType="candlestick"
/>
```

### ReactFinancialChart (Advanced Technical Analysis)

```typescript
import ReactFinancialChart from '@/components/market-data/ReactFinancialChart';

<ReactFinancialChart
  data={ohlcData}
  symbol="AAPL"
  indicators={['SMA', 'EMA', 'RSI']}
  drawingTools={true}
/>
```

## Error Handling

### API Errors

```typescript
// Handled automatically in custom hooks via onError callback
const createMutation = useMutation({
  mutationFn: createData,
  onError: (error) => {
    showError(`Creation failed: ${error.message}`);
    // Error is also available in component
  },
});

// In component
const { createExample, error } = useExample();
if (error) {
  console.error("Error:", error);
}
```

### Loading States

```typescript
const { data, isLoading, isError, error } = useQuery({...});

if (isLoading) return <CircularProgress />;
if (isError) return <ErrorComponent error={error} />;
return <DataComponent data={data} />;
```

### User Feedback

```typescript
// Always use Snackbar for user feedback (NOT console.log or alert)
const { showSuccess, showError, showInfo, showWarning } = useSnackbar();

try {
  await someAction();
  showSuccess("작업이 완료되었습니다.");
} catch (error) {
  showError(`작업 실패: ${error.message}`);
}
```

## Testing Patterns

### Component Testing (Future)

```typescript
import { render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: false },
  },
});

test('renders example list', async () => {
  render(
    <QueryClientProvider client={queryClient}>
      <ExampleList />
    </QueryClientProvider>
  );

  await waitFor(() => {
    expect(screen.getByText('Example 1')).toBeInTheDocument();
  });
});
```

### Hook Testing (Future)

```typescript
import { renderHook, waitFor } from "@testing-library/react";
import { useExample } from "@/hooks/useExample";

test("fetches example list", async () => {
  const { result } = renderHook(() => useExample());

  await waitFor(() => {
    expect(result.current.exampleList).toBeDefined();
  });
});
```

## Performance Optimization

### TanStack Query Caching

```typescript
// Adjust staleTime and gcTime based on data volatility
useQuery({
  queryKey: ["examples"],
  queryFn: fetchExamples,
  staleTime: 1000 * 60 * 5, // 5 min - data considered fresh
  gcTime: 30 * 60 * 1000, // 30 min - cache retention
  refetchOnWindowFocus: true, // Auto-refetch on focus
  refetchOnMount: true, // Refetch on component mount
});
```

### Lazy Loading

```typescript
// Dynamic imports for large components
import dynamic from 'next/dynamic';

const HeavyChart = dynamic(
  () => import('@/components/market-data/HeavyChart'),
  { ssr: false, loading: () => <CircularProgress /> }
);
```

### useMemo for Derived State

```typescript
import { useMemo } from "react";

const filteredData = useMemo(() => {
  return data?.filter((item) => item.status === "active");
}, [data]);
```

## Code Quality Standards

### TypeScript

- **Use strict types** - NO `any` types
- **Import types** from `@/client/types.gen.ts`
- **Define interfaces** for component props
- **Use type guards** for runtime type checking

```typescript
// ✅ Good
import type { Backtest, BacktestCreate } from "@/client";

interface Props {
  backtest: Backtest;
  onUpdate: (data: BacktestCreate) => void;
}

// ❌ Bad
interface Props {
  backtest: any;
  onUpdate: (data: any) => void;
}
```

### Biome Linting

```bash
# Check code
pnpm lint

# Auto-fix issues
pnpm lint:fix

# Format code
pnpm format
```

### Component Guidelines

- **File size**: Keep under 500 lines
- **Reusable logic**: Extract to custom hooks
- **Common UI**: Move to `components/common/`
- **Client components**: Add `'use client'` directive when needed
- **Prop destructuring**: Use destructuring for better readability

## Common Pitfalls

### ❌ DON'T: Edit Auto-generated Client

```typescript
// ❌ WRONG - Editing src/client/sdk.gen.ts
export class BacktestService {
  // ... manually added code (will be overwritten)
}
```

### ✅ DO: Use Wrapper Hooks

```typescript
// ✅ CORRECT - Create custom hook wrapper
export function useBacktest() {
  // Your custom logic using BacktestService
}
```

### ❌ DON'T: Use Direct API Calls in Components

```typescript
// ❌ WRONG
import { BacktestService } from "@/client";

function MyComponent() {
  const handleCreate = async () => {
    await BacktestService.createBacktest({ body: data });
  };
}
```

### ✅ DO: Use Custom Hooks

```typescript
// ✅ CORRECT
import { useBacktest } from "@/hooks/useBacktests";

function MyComponent() {
  const { createBacktest } = useBacktest();

  const handleCreate = async () => {
    await createBacktest(data);
  };
}
```

### ❌ DON'T: Ignore Loading States

```typescript
// ❌ WRONG
const { data } = useQuery({...});
return <div>{data.name}</div>; // Crashes if data is undefined
```

### ✅ DO: Handle Loading States

```typescript
// ✅ CORRECT
const { data, isLoading } = useQuery({...});
if (isLoading) return <CircularProgress />;
return <div>{data?.name}</div>;
```

### ❌ DON'T: Use console.log for User Feedback

```typescript
// ❌ WRONG
try {
  await deleteItem();
  console.log("Deleted successfully");
} catch (error) {
  console.error(error);
}
```

### ✅ DO: Use Snackbar

```typescript
// ✅ CORRECT
const { showSuccess, showError } = useSnackbar();

try {
  await deleteItem();
  showSuccess("삭제되었습니다.");
} catch (error) {
  showError(`삭제 실패: ${error.message}`);
}
```

### ❌ DON'T: Forget to Invalidate Queries

```typescript
// ❌ WRONG - Cache not updated
const deleteMutation = useMutation({
  mutationFn: deleteItem,
  onSuccess: () => {
    showSuccess("삭제되었습니다.");
    // Cache is stale!
  },
});
```

### ✅ DO: Invalidate Related Queries

```typescript
// ✅ CORRECT - Cache automatically refreshed
const deleteMutation = useMutation({
  mutationFn: deleteItem,
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ["items"] });
    showSuccess("삭제되었습니다.");
  },
});
```

## Environment Variables

```bash
# .env.local
NEXT_PUBLIC_API_BASE_URL=http://localhost:8500

# Usage in code
const apiUrl = process.env.NEXT_PUBLIC_API_BASE_URL;
```

## Quick Reference

### Essential Commands

| Command           | Purpose                      |
| ----------------- | ---------------------------- |
| `pnpm dev`        | Start dev server (port 3000) |
| `pnpm build`      | Production build             |
| `pnpm start`      | Run production server        |
| `pnpm lint`       | Run Biome linter             |
| `pnpm lint:fix`   | Auto-fix lint issues         |
| `pnpm format`     | Format code with Biome       |
| `pnpm gen:client` | Regenerate API client        |

### File Locations

| Purpose    | Location                                  |
| ---------- | ----------------------------------------- |
| Pages      | `src/app/(main)/` or `src/app/(auth)/`    |
| Components | `src/components/{domain}/`                |
| Hooks      | `src/hooks/use{Domain}.ts`                |
| Contexts   | `src/contexts/{Name}Context.tsx`          |
| Types      | `src/types/` or `src/client/types.gen.ts` |
| Utils      | `src/utils/`                              |
| API Client | `src/client/` (auto-generated)            |
| Config     | `runtimeConfig.ts`, `next.config.mjs`     |

### Import Aliases

| Alias          | Path              |
| -------------- | ----------------- |
| `@/`           | `src/`            |
| `@/client`     | `src/client/`     |
| `@/components` | `src/components/` |
| `@/hooks`      | `src/hooks/`      |
| `@/contexts`   | `src/contexts/`   |
| `@/types`      | `src/types/`      |
| `@/utils`      | `src/utils/`      |

## Architecture Diagrams

### Request Flow

```
User Action
  ↓
Component
  ↓
Custom Hook (useExample)
  ↓
TanStack Query (useQuery/useMutation)
  ↓
Hey-API Service (ExampleService)
  ↓
HTTP Client (with cookies)
  ↓
Backend API (Port 8500)
  ↓
Response → Cache Update → UI Refresh
```

### Authentication Flow

```
1. User submits login form
2. Component calls useAuth().login()
3. AuthContext sends POST /api/auth/login (Next.js API route)
4. API route proxies to Backend POST /auth/login
5. Backend validates credentials → Sets JWT cookie
6. Frontend receives cookie → Updates AuthContext
7. AuthContext fetches GET /users/me → User info
8. Redirect to protected route
```

### State Management Flow

```
Server State (TanStack Query)
  ├─ Queries: Data fetching & caching
  │   └─ useQuery → Automatic background updates
  └─ Mutations: Data modification
      └─ useMutation → Optimistic updates & cache invalidation

Client State (React Context)
  ├─ AuthContext: Authentication & user info
  ├─ SnackbarContext: Notifications
  └─ SidebarContext: UI state

Local State (useState)
  └─ Component-specific temporary state
```

## Related Documentation

- [Frontend README](./README.md) - Comprehensive frontend documentation
- [Backend AGENTS.md](../backend/AGENTS.md) - Backend development guide
- [AUTH_FLOW.md](../AUTH_FLOW.md) - Detailed authentication flow
- [User Stories](../docs/USER_STORIES.md) - Product requirements

## Debugging Tips

### TanStack Query DevTools

```typescript
// Add to QueryProvider.tsx (development only)
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';

<QueryClientProvider client={queryClient}>
  {children}
  <ReactQueryDevtools initialIsOpen={false} />
</QueryClientProvider>
```

### Network Requests

```bash
# Check if backend is running
curl http://localhost:8500/health

# View OpenAPI schema
curl http://localhost:8500/openapi.json | jq

# Test authentication
curl -i -X POST http://localhost:8500/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test"}'
```

### Browser DevTools

- **Network Tab**: Check API requests/responses
- **Application → Cookies**: Verify JWT cookie exists
- **Console**: Check for React errors
- **Components**: React DevTools for component tree

### Common Issues

**Issue**: "Module not found" error after `pnpm gen:client` **Solution**:
Restart Next.js dev server

**Issue**: Authentication not working **Solution**: Check cookie in Application
tab, verify backend is running on 8500

**Issue**: Type errors in auto-generated client **Solution**: Regenerate client
with `pnpm gen:client`, check OpenAPI schema validity

**Issue**: Query not refetching after mutation **Solution**: Ensure
`queryClient.invalidateQueries()` is called in mutation onSuccess

---

This guide provides essential patterns and practices for AI agents working on
the frontend. Always prioritize custom hooks, type safety, and user feedback
through Snackbar notifications.
