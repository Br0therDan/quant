import {
  BacktestService,
  type BacktestCreate,
  type BacktestUpdate,
} from "@/client";
import { useSnackbar } from "@/contexts/SnackbarContext";
import {
  useMutation,
  useQuery,
  useQueryClient,
  type UseMutateAsyncFunction,
  type UseMutateFunction,
} from "@tanstack/react-query";
import { useMemo } from "react";

type UpdateBacktestVariables = {
  id: string;
  updateData: Partial<BacktestUpdate>;
};

type CreateBacktestFn = UseMutateFunction<
  Awaited<ReturnType<typeof BacktestService.createBacktest>>["data"],
  unknown,
  BacktestCreate,
  unknown
>;

type UpdateBacktestFn = UseMutateFunction<
  Awaited<ReturnType<typeof BacktestService.updateBacktest>>["data"],
  unknown,
  UpdateBacktestVariables,
  unknown
>;

type DeleteBacktestFn = UseMutateFunction<
  Awaited<ReturnType<typeof BacktestService.deleteBacktest>>["data"],
  unknown,
  string,
  unknown
>;

export const backtestQueryKeys = {
  all: ["backtest"] as const,
  lists: () => [...backtestQueryKeys.all, "list"] as const,
  list: (filters: string) => [...backtestQueryKeys.lists(), { filters }] as const,
  details: () => [...backtestQueryKeys.all, "detail"] as const,
  detail: (id: string) => [...backtestQueryKeys.details(), id] as const,
  results: () => [...backtestQueryKeys.all, "result"] as const,
  result: (id: string) => [...backtestQueryKeys.results(), id] as const,
  analytics: () => [...backtestQueryKeys.all, "analytics"] as const,
  performanceState: () => [...backtestQueryKeys.analytics(), "performanceState"] as const,
  tradeState: () => [...backtestQueryKeys.analytics(), "tradeState"] as const,
  summaryState: () => [...backtestQueryKeys.analytics(), "summaryState"] as const,
  healthState: () => [...backtestQueryKeys.all, "healthState"] as const,
} as const;

export function useBacktest() {
  const queryClient = useQueryClient();
  const { showSuccess, showError } = useSnackbar();

  const backtestListQuery = useQuery({
    queryKey: backtestQueryKeys.lists(),
    queryFn: async () => {
      const response = await BacktestService.getBacktests();
      return response.data;
    },
    staleTime: 1000 * 60 * 5,
    gcTime: 30 * 60 * 1000,
  });

  // Health check endpoint
  const backtestHealthCheckQuery = useQuery({
    queryKey: backtestQueryKeys.healthState(),
    queryFn: async () => {
      const response = await BacktestService.healthCheck();
      return response.data;
    },
    staleTime: 1000 * 60 * 5,
    gcTime: 30 * 60 * 1000,
  });

  const createBacktestMutation = useMutation({
    mutationFn: async (data: BacktestCreate) => {
      const response = await BacktestService.createBacktest({ body: data });
      return response.data;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: backtestQueryKeys.lists() });
      showSuccess(
        `백테스트 "${data?.name || "새 백테스트"}"가 성공적으로 생성되었습니다`,
      );
    },
    onError: (error) => {
      console.error("백테스트 생성 실패:", error);
      showError(
        error instanceof Error
          ? error.message
          : "백테스트 생성에 실패했습니다",
      );
    },
  });

  const updateBacktestMutation = useMutation({
    mutationFn: async ({ id, updateData }: UpdateBacktestVariables) => {
      const response = await BacktestService.updateBacktest({
        path: { backtest_id: id },
        body: updateData,
      });
      return response.data;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: backtestQueryKeys.lists() });
      if (data?.id) {
        queryClient.invalidateQueries({ queryKey: backtestQueryKeys.detail(data.id) });
      }
      showSuccess(
        `백테스트 "${data?.name || "백테스트"}"가 성공적으로 업데이트되었습니다`,
      );
    },
    onError: (error) => {
      console.error("백테스트 업데이트 실패:", error);
      showError(
        error instanceof Error
          ? error.message
          : "백테스트 업데이트에 실패했습니다",
      );
    },
  });

  const deleteBacktestMutation = useMutation({
    mutationFn: async (id: string) => {
      const response = await BacktestService.deleteBacktest({
        path: { backtest_id: id },
      });
      return response.data;
    },
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: backtestQueryKeys.lists() });
      queryClient.removeQueries({ queryKey: backtestQueryKeys.detail(id) });
      showSuccess("백테스트가 성공적으로 삭제되었습니다");
    },
    onError: (error) => {
      console.error("백테스트 삭제 실패:", error);
      showError(
        error instanceof Error
          ? error.message
          : "백테스트 삭제에 실패했습니다",
      );
    },
  });

  const executeBacktestMutation = useMutation({
    mutationFn: async ({
      backtestId,
      signals,
    }: {
      backtestId: string;
      signals: Array<{ [key: string]: unknown }>;
    }) => {
      const response = await BacktestService.executeBacktest({
        path: { backtest_id: backtestId },
        body: { signals },
      });
      return response.data;
    },
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: backtestQueryKeys.lists() });
      queryClient.invalidateQueries({
        queryKey: backtestQueryKeys.detail(variables.backtestId),
      });
      showSuccess("백테스트 실행이 시작되었습니다");
    },
    onError: (error) => {
      console.error("백테스트 실행 실패:", error);
      showError(
        error instanceof Error
          ? error.message
          : "백테스트 실행에 실패했습니다",
      );
    },
  });

  return useMemo(
    () => ({
      backtestList: backtestListQuery.data,
      backtestHealthCheck: backtestHealthCheckQuery.data,
      isError: {
        backtestList: backtestListQuery.isError,
        backtestHealthCheck: backtestHealthCheckQuery.isError,
      },
      isLoading: {
        backtestList: backtestListQuery.isLoading,
        backtestHealthCheck: backtestHealthCheckQuery.isLoading,
      },
      isMutating: {
        createBacktest: createBacktestMutation.isPending,
        updateBacktest: updateBacktestMutation.isPending,
        deleteBacktest: deleteBacktestMutation.isPending,
        executeBacktest: executeBacktestMutation.isPending,
      },
      createBacktest: createBacktestMutation.mutate as CreateBacktestFn,
      createBacktestAsync:
        createBacktestMutation.mutateAsync as UseMutateAsyncFunction<
          Awaited<ReturnType<typeof BacktestService.createBacktest>>["data"],
          unknown,
          BacktestCreate,
          unknown
        >,
      updateBacktest: updateBacktestMutation.mutate as UpdateBacktestFn,
      updateBacktestAsync:
        updateBacktestMutation.mutateAsync as UseMutateAsyncFunction<
          Awaited<ReturnType<typeof BacktestService.updateBacktest>>["data"],
          unknown,
          UpdateBacktestVariables,
          unknown
        >,
      deleteBacktest: deleteBacktestMutation.mutate as DeleteBacktestFn,
      deleteBacktestAsync:
        deleteBacktestMutation.mutateAsync as UseMutateAsyncFunction<
          Awaited<ReturnType<typeof BacktestService.deleteBacktest>>["data"],
          unknown,
          string,
          unknown
        >,
      executeBacktest: executeBacktestMutation.mutate,
      executeBacktestAsync: executeBacktestMutation.mutateAsync,
      refetch: {
        list: backtestListQuery.refetch,
        health: backtestHealthCheckQuery.refetch,
      },
    }),
    [
      backtestHealthCheckQuery,
      backtestListQuery,
      createBacktestMutation,
      deleteBacktestMutation,
      executeBacktestMutation,
      updateBacktestMutation,
    ],
  );
}

export const useBacktestDetail = (id: string) =>
  useQuery({
    queryKey: backtestQueryKeys.detail(id),
    queryFn: async () => {
      const response = await BacktestService.getBacktest({
        path: { backtest_id: id },
      });
      return response.data;
    },
    enabled: !!id,
    staleTime: 1000 * 60 * 5,
    gcTime: 30 * 60 * 1000,
  });
